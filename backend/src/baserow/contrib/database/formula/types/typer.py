from copy import deepcopy
from typing import Dict, Optional, List

from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
    FieldNode,
    FieldEdge,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
)
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_django_expression,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaType,
)
from baserow.contrib.database.formula.types.typed_field_updater import (
    _recreate_field_if_required,
)
from baserow.contrib.database.formula.types.visitors import (
    TypeAnnotatingASTVisitor,
)
from baserow.contrib.database.views.handler import ViewHandler


class TypedFieldNode:
    def __init__(
        self,
        typed_expression: BaserowExpression[BaserowFormulaType],
        field_node: FieldNode,
        field: Optional[Field],
    ):
        self.typed_expression = typed_expression
        self.field_node = field_node
        self.field = field


class TypedBaserowFields:
    def __init__(self):
        self.typed_fields: Dict[str, TypedFieldNode] = {}
        self.fields_needing_values_refresh: List[TypedFieldNode] = []

    def add_node(self, typed_node: TypedFieldNode, values_refresh_needed=False):
        name = typed_node.field_node.unique_name()
        if self.has(name):
            raise Exception(f"Already have {name}?")
        self.typed_fields[name] = typed_node
        if values_refresh_needed:
            self.fields_needing_values_refresh.append(typed_node)

    def has(self, name):
        return name in self.typed_fields

    def get(self, name):
        return self.typed_fields[name]

    def updated_fields(self, exclude_field=None):
        return [
            typed_field.field
            for typed_field in self.fields_needing_values_refresh
            if exclude_field is not None and typed_field.field != exclude_field
        ]

    def refresh_fields(self):
        latest_table_query = {}
        current_table = None
        model_cache = {}

        for typed_field in self.fields_needing_values_refresh:

            field = typed_field.field
            if current_table is None:
                current_table = field.table

            # The next field to refresh is not part of the table we've been building up
            # a bulk update statement for. So we evaluate that bulk update and start
            # building up a new update for this new table
            if current_table != field.table:
                model_cache[current_table.id].objects_and_trash.update(
                    **latest_table_query
                )
                current_table = field.table
                latest_table_query = {}

            if current_table.id not in model_cache:
                model_cache[current_table.id] = current_table.get_model()

            expr = baserow_expression_to_django_expression(
                typed_field.typed_expression, model_cache[current_table.id], None
            )
            if expr is not None and not (field.error or field.trashed):
                latest_table_query[field.db_column] = expr

        if current_table is not None:
            model_cache[current_table.id].objects_and_trash.update(**latest_table_query)


def _type_and_substitute_formula_field(
    formula_field: FormulaField,
    formula_field_node: FieldNode,
    already_typed_fields: TypedBaserowFields,
    update_graph: bool,
):
    untyped_expression = raw_formula_to_untyped_expression(formula_field.formula)
    typed_expr: BaserowExpression[BaserowFormulaType] = untyped_expression.accept(
        TypeAnnotatingASTVisitor(formula_field_node, already_typed_fields, update_graph)
    )

    merged_expression_type = (
        typed_expr.expression_type.new_type_with_user_and_calculated_options_merged(
            formula_field
        )
    )
    # Take into account any user set formatting options on this formula field.
    typed_expr_merged_with_user_options = typed_expr.with_type(merged_expression_type)

    wrapped_typed_expr = (
        typed_expr_merged_with_user_options.expression_type.wrap_at_field_level(
            typed_expr_merged_with_user_options
        )
    )

    return TypedFieldNode(wrapped_typed_expr, formula_field_node, formula_field)


def type_and_update_field(
    field: Field,
    raise_if_invalid: bool,
    recreate_field_if_needed: bool,
    fix_invalid_references: bool,
    update_graph: bool,
    values_refresh_needed: bool,
    fields_so_far: Optional[TypedBaserowFields] = None,
    force_update: bool = False,
):
    if fields_so_far is None:
        fields_so_far = TypedBaserowFields()

    node = field.get_or_create_node()
    if fields_so_far.has(node.unique_name()):
        return

    update_needed = False
    if isinstance(field, FormulaField):
        update_needed = _type_formula_field(
            field,
            fields_so_far,
            raise_if_invalid,
            recreate_field_if_needed,
            update_graph,
            values_refresh_needed or force_update,
        )

    if fix_invalid_references:
        any_fixed = _fix_invalid_refs(field, node)
        update_needed = update_needed or any_fixed

    if update_needed or force_update:
        fields_needing_update = node.descendants(max_depth=1)
        for direct_descendant in fields_needing_update:
            type_and_update_field(
                direct_descendant.field.specific,
                False,
                True,
                False,
                update_graph,
                True,
                fields_so_far,
                force_update=force_update,
            )
    return fields_so_far


def _type_formula_field(
    formula_field: FormulaField,
    fields_so_far: TypedBaserowFields,
    raise_if_invalid: bool,
    recreate_field_if_needed: bool,
    update_graph: bool,
    values_refresh_needed: bool,
):
    typed_formula_field_node = type_formula_field(
        formula_field, fields_so_far, update_graph
    )
    original = deepcopy(formula_field)
    expression = typed_formula_field_node.typed_expression
    expression_type = expression.expression_type
    if raise_if_invalid:
        expression_type.raise_if_invalid()
    expression_type.persist_onto_formula_field(formula_field)
    formula_field.internal_typed_formula = str(expression)

    updated = False
    if not original.same_as(formula_field):
        updated = True
        formula_field.save()
        ViewHandler().field_type_changed(formula_field)
        if recreate_field_if_needed:
            _recreate_field_if_required(
                formula_field.table, original, expression_type, formula_field
            )

    fields_so_far.add_node(
        typed_formula_field_node, values_refresh_needed=values_refresh_needed or updated
    )
    return updated


def _fix_invalid_refs(field, node):
    try:
        invalid_node_with_our_name = FieldNode.objects.get(
            table=field.table,
            field__isnull=True,
            unresolved_field_name=field.name,
        )
        new_children = FieldEdge.objects.filter(parent=invalid_node_with_our_name)
        new_children.update(parent=node)
        invalid_node_with_our_name.delete()
        return True
    except FieldNode.DoesNotExist:
        return False


def type_formula_field(
    formula_field: FormulaField,
    already_typed_fields: TypedBaserowFields,
    update_graph: bool,
):
    try:
        node = formula_field.get_or_create_node()
        if update_graph:
            # Delete all existing dependencies this formula_field has as we are about
            # to recreate them
            parent_edges = FieldEdge.objects.filter(child=node)
            # We might have deleted the last edge of an invalid reference. So check
            # and delete it if so.
            for edge in parent_edges.all():
                print(
                    f"Deleted dep of {edge.child.unique_name()} to "
                    f"{edge.parent.unique_name()}"
                )
                if edge.parent.is_unused_invalid_ref():
                    edge.parent.delete()
            parent_edges.delete()

        typed_formula_field_node = _type_and_substitute_formula_field(
            formula_field, node, already_typed_fields, update_graph
        )
        return typed_formula_field_node
    except RecursionError:
        raise MaximumFormulaSizeError()


def type_and_update_fields(fields: List[Field]):
    typed_fields = TypedBaserowFields()
    for f in fields:
        type_and_update_field(f, False, True, False, True, True, typed_fields)
    return typed_fields
