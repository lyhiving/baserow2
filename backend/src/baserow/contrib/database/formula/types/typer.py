from typing import Dict, Optional, List, Union

from django.conf import settings

from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFieldReference,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowIntegerLiteral,
    BaserowDecimalLiteral,
    BaserowBooleanLiteral,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.models import (
    FieldDependencyEdge,
    FieldDependencyNode,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.exceptions import (
    NoCircularReferencesError,
    NoSelfReferencesError,
)
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaType,
    UnTyped,
    BaserowFormulaValidType,
)
from baserow.contrib.database.formula.types.formula_types import (
    BaserowFormulaTextType,
    BaserowFormulaNumberType,
    BaserowFormulaBooleanType,
)
from baserow.contrib.database.table import models


class TypedFieldDependencyNode:
    def __init__(
        self,
        typed_expression: BaserowExpression[BaserowFormulaType],
        field_node: FieldDependencyNode,
        field,
    ):
        self.typed_expression = typed_expression
        self.field_node = field_node
        self.field = field


class TypedBaserowFields:
    """
    A collection of Fields which have been typed. Some of the fields may need a values
    refresh due to a change in a dependant field which can be triggered by calling
    refresh_fields.
    """

    def __init__(self):
        self.typed_fields: Dict[str, TypedFieldDependencyNode] = {}
        self.fields_needing_values_refresh: List[TypedFieldDependencyNode] = []
        self.fields_needing_save: List[TypedFieldDependencyNode] = []

    def _unique_name_for_table_and_field_name(
        self, table: "models.Table", field_name: str
    ):
        return f"{str(table.id)}_{field_name}"

    def _unique_name_for_node(
        self, node: Union[TypedFieldDependencyNode, FieldDependencyNode]
    ):
        if isinstance(node, TypedFieldDependencyNode):
            node = node.field_node
        table = node.table
        if node.is_reference_to_real_field():
            return self._unique_name_for_table_and_field_name(table, node.field.name)
        else:
            return self._unique_name_for_table_and_field_name(
                table, node.broken_reference_field_name
            )

    def add_typed_field_node(
        self, typed_node: TypedFieldDependencyNode, values_refresh_needed=False
    ):
        unique_name = self._unique_name_for_node(typed_node)
        if unique_name in self.typed_fields:
            raise Exception(f"Already have {unique_name}?")
        self.typed_fields[unique_name] = typed_node
        if values_refresh_needed:
            self.fields_needing_values_refresh.append(typed_node)

    def updated_fields(self, exclude_field=None):
        return [
            typed_field.field
            for typed_field in self.fields_needing_values_refresh
            if exclude_field is not None and typed_field.field != exclude_field
        ]

    def refresh_fields(self, starting_field):
        fields = self.fields_needing_values_refresh

    def get_field(self, table: "models.Table", field_name: str):
        unique_name = self._unique_name_for_table_and_field_name(table, field_name)
        try:
            return self.typed_fields[unique_name]
        except KeyError:
            return None

    def already_has_field(self, field):
        return (
            self._unique_name_for_node(field.get_or_create_node()) in self.typed_fields
        )


def type_and_update_field(
    field,
    already_typed_fields: Optional[TypedBaserowFields] = None,
):
    from baserow.contrib.database.fields.registries import field_type_registry

    if already_typed_fields is None:
        already_typed_fields = TypedBaserowFields()

    if already_typed_fields.already_has_field(field):
        return

    field_type = field_type_registry.get_by_model(field)
    if field_type.type == "formula":
        typed_formula_field_node = type_formula_field(field, already_typed_fields, True)
        already_typed_fields.add_typed_field_node(
            typed_formula_field_node, values_refresh_needed=True
        )

    _fix_invalid_refs(field)

    fields_needing_update = field.get_or_create_node().descendants(max_depth=1)
    for direct_descendant in fields_needing_update:
        type_and_update_field(
            direct_descendant.field.specific,
            already_typed_fields,
        )
    return already_typed_fields


def _fix_invalid_refs(field):
    try:
        invalid_node_with_our_name = FieldDependencyNode.objects.get(
            table=field.table,
            field__isnull=True,
            broken_reference_field_name=field.name,
        )
        new_children = FieldDependencyEdge.objects.filter(
            parent=invalid_node_with_our_name
        )
        new_children.update(parent=field.get_or_create_node())
        invalid_node_with_our_name.delete()
        return True
    except FieldDependencyNode.DoesNotExist:
        return False


def type_formula_field(
    formula_field,
    already_typed_fields: TypedBaserowFields,
    update_graph: bool,
):
    try:
        untyped_expression = raw_formula_to_untyped_expression(formula_field.formula)

        typed_expr = type_and_optionally_graph_formula_field(
            formula_field, untyped_expression, already_typed_fields, update_graph
        )

        merged_expression_type = (
            typed_expr.expression_type.new_type_with_user_and_calculated_options_merged(
                formula_field
            )
        )

        # Take into account any user set formatting options on this formula field.
        typed_expr_merged_with_user_options = typed_expr.with_type(
            merged_expression_type
        )

        wrapped_typed_expr = (
            typed_expr_merged_with_user_options.expression_type.wrap_at_field_level(
                typed_expr_merged_with_user_options
            )
        )

        return TypedFieldDependencyNode(
            wrapped_typed_expr, formula_field.get_or_create_node(), formula_field
        )
    except RecursionError:
        raise MaximumFormulaSizeError()


def type_and_update_fields(fields):
    typed_fields = TypedBaserowFields()
    for f in fields:
        type_and_update_field(f, typed_fields)
    return typed_fields


def type_and_optionally_graph_formula_field(
    formula_field,
    untyped_expression: BaserowExpression[UnTyped],
    already_typed_fields: TypedBaserowFields,
    update_graph: bool,
) -> BaserowExpression[BaserowFormulaType]:
    field_node = formula_field.get_or_create_node()
    if update_graph:
        # Delete all existing dependencies this formula_field has as we are about
        # to recreate them
        parent_edges = FieldDependencyEdge.objects.filter(child=field_node)
        # We might have deleted the last edge of an invalid reference. So check
        # and delete it if so.
        for edge in parent_edges.all():
            if edge.parent.is_broken_reference_with_no_dependencies():
                edge.parent.delete()
        parent_edges.delete()

    return untyped_expression.accept(
        TypingAndGraphingVisitor(field_node, already_typed_fields, update_graph)
    )


class TypingAndGraphingVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(
        self,
        field_node_being_typed,
        already_typed_fields: TypedBaserowFields,
        update_graph: bool,
    ):
        self.field_node_being_typed = field_node_being_typed
        self.already_typed_fields = already_typed_fields
        self.update_graph = update_graph

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:

        self._raise_if_self_reference(field_reference)

        typed_node = _calculate_expression_and_node_from_field_reference(
            self.field_node_being_typed.table,
            field_reference,
            self.already_typed_fields,
        )

        self._optionally_add_graph_dependency_raising_if_circular(typed_node)

        return typed_node.typed_expression

    def _optionally_add_graph_dependency_raising_if_circular(
        self, typed_node: TypedFieldDependencyNode
    ):
        referenced_field_dependency_node = typed_node.field_node
        if (
            self.field_node_being_typed
            not in referenced_field_dependency_node.self_and_ancestors(
                max_depth=settings.MAX_FIELD_REFERENCE_DEPTH
            )
        ):
            if self.update_graph:
                referenced_field_dependency_node.add_child(
                    self.field_node_being_typed, disable_circular_check=True
                )
        else:
            raise NoCircularReferencesError()

    def _raise_if_self_reference(self, field_reference):
        field_name = self.field_node_being_typed.field.name
        if field_name == field_reference.referenced_field_name:
            raise NoSelfReferencesError()

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return string_literal.with_valid_type(BaserowFormulaTextType())

    def visit_function_call(
        self, function_call: BaserowFunctionCall[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        typed_args: List[BaserowExpression[BaserowFormulaValidType]] = []
        for expr in function_call.args:
            typed_args.append(expr.accept(self))
        return function_call.type_function_given_typed_args(typed_args)

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return int_literal.with_valid_type(
            BaserowFormulaNumberType(
                number_decimal_places=0,
            ),
        )

    def visit_decimal_literal(
        self, decimal_literal: BaserowDecimalLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return decimal_literal.with_valid_type(
            BaserowFormulaNumberType(
                number_decimal_places=decimal_literal.num_decimal_places()
            )
        )

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return boolean_literal.with_valid_type(BaserowFormulaBooleanType())


def _calculate_expression_and_node_from_field_reference(
    table, field_reference, already_typed_fields
) -> TypedFieldDependencyNode:
    # TODO
    from baserow.contrib.database.fields.models import Field

    referenced_field_name = field_reference.referenced_field_name
    typed_field_node = already_typed_fields.get_field(table, referenced_field_name)

    if typed_field_node is None:
        try:
            typed_field_node = _lookup_expression_and_node_from_db(
                already_typed_fields, referenced_field_name, table
            )
        except Field.DoesNotExist:
            typed_field_node = _construct_broken_reference_node(
                field_reference, referenced_field_name, table
            )
        already_typed_fields.add_typed_field_node(typed_field_node)

    return typed_field_node


def _construct_broken_reference_node(field_reference, referenced_field_name, table):
    node, _ = FieldDependencyNode.objects.get_or_create(
        table=table,
        broken_reference_field_name=referenced_field_name,
    )
    return TypedFieldDependencyNode(
        field_reference.with_invalid_type(
            f"references the deleted or unknown field "
            f"{field_reference.referenced_field_name}"
        ),
        node,
        None,
    )


def _lookup_expression_and_node_from_db(
    already_typed_fields, referenced_field_name, table
):
    from baserow.contrib.database.fields.registries import field_type_registry

    referenced_field = table.field_set.get(name=referenced_field_name).specific
    field_type = field_type_registry.get_by_model(referenced_field)
    expr = field_type.to_baserow_formula_expression(
        referenced_field, already_typed_fields
    )
    typed_field_node = TypedFieldDependencyNode(
        expr, referenced_field.get_or_create_node(), referenced_field
    )
    return typed_field_node
