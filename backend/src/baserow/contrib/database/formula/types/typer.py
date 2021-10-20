import typing
from collections import OrderedDict
from copy import deepcopy
from typing import Dict, Optional, Set, List, OrderedDict as OrderedDictType

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
    FieldNode,
    FieldEdge,
)
from baserow.contrib.database.fields.registries import field_type_registry, FieldType
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFunctionDefinition,
    BaserowFieldReference,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.exceptions import (
    NoSelfReferencesError,
    NoCircularReferencesError,
)
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
)
from baserow.contrib.database.formula.types.formula_types import (
    BASEROW_FORMULA_TYPE_ALLOWED_FIELDS,
)
from baserow.contrib.database.formula.types.typed_field_updater import (
    _recreate_field_if_required,
)
from baserow.contrib.database.formula.types.visitors import (
    FieldReferenceResolvingVisitor,
    TypeAnnotatingASTVisitor,
    SubstituteFieldWithThatFieldsExpressionVisitor,
    FunctionsUsedVisitor,
)
from baserow.contrib.database.table import models
from baserow.contrib.database.views.handler import ViewHandler


class TypedFieldNode:
    def __init__(
        self,
        typed_expression: BaserowExpression[BaserowFormulaType],
        field_node: FieldNode,
    ):
        self.typed_expression = typed_expression
        self.field_node = field_node


# class UntypedFormulaFieldWithReferences:
#     """
#     A graph node class, containing a formula field and it's untyped but parsed
#     BaserowExpression, references to it's child and parent fields and it's formula
#     field.
#     """
#
#     def __init__(
#         self,
#         original_formula_field: FormulaField,
#         untyped_expression: BaserowExpression[UnTyped],
#     ):
#         self.original_formula_field = original_formula_field
#         self.untyped_expression = untyped_expression
#         self.parents: Dict[str, "UntypedFormulaFieldWithReferences"] = {}
#         self.formula_children: Dict[str, "UntypedFormulaFieldWithReferences"] = {}
#         self.field_children: Set[str] = set()
#
#     @property
#     def field_name(self):
#         return self.original_formula_field.name
#
#     def add_child_formulas_and_raise_if_self_ref_found(
#         self, child_formula: "UntypedFormulaFieldWithReferences"
#     ):
#         """
#         Registers itself as a parent with the provided child field and also stores it
#         as a child.
#
#         :param child_formula: The new child to register to this node.
#         """
#
#         if child_formula.field_name == self.field_name:
#             raise NoSelfReferencesError()
#         self.formula_children[child_formula.field_name] = child_formula
#         child_formula.parents[self.field_name] = self
#
#     def add_child_field(self, child):
#         self.field_children.add(child)
#
#     def add_all_children_depth_first_order_raise_for_circular_ref(
#         self,
#         visited_so_far: OrderedDictType[str, "UntypedFormulaFieldWithReferences"],
#         ordered_formula_fields: OrderedDictType[
#             str, "UntypedFormulaFieldWithReferences"
#         ],
#     ):
#         """
#         Searches down the field graph and adds all children in a depth first order to
#         the provided list of ordered_formula_fields. In other words all children
#         will be added to the ordered_formula_fields list before their parents.
#
#         :param visited_so_far: An ordered dict containing all fields already visited
#             , used to check to see if we have already visited a node in the field graph
#             and if so will raise a NoCircularReferencesError.
#         :param ordered_formula_fields: The output list of fields ordered such that all
#             children appear in the list before their parents.
#         """
#
#         if self.field_name in visited_so_far:
#             raise NoCircularReferencesError(
#                 [f.field_name for f in visited_so_far.values()] + [self.field_name]
#             )
#
#         visited_so_far[self.field_name] = self
#         if self.field_name in ordered_formula_fields:
#             return
#         for formula_child in self.formula_children.values():
#             formula_child.add_all_children_depth_first_order_raise_for_circular_ref(
#                 visited_so_far.copy(),
#                 ordered_formula_fields,
#             )
#         ordered_formula_fields[self.field_name] = self
#
#     def to_typed(
#         self,
#         typed_expression: BaserowExpression[BaserowFormulaType],
#         field_name_to_typed_field: Dict[str, "TypedFieldWithReferences"],
#     ) -> "TypedFieldWithReferences":
#         """
#         Given a typed expression for this field generates a TypedFieldWithReferences
#         graph node.
#
#         :param typed_expression: The typed expression for this field.
#         :param field_name_to_typed_field: A dictionary of field name to other
#             TypedFieldWithReferences which must already contain all child fields of this
#             field.
#         :return: A new TypedFieldWithReferences based off this field.
#         """
#
#         updated_formula_field = self._create_untyped_copy_of_original_field()
#
#         functions_used: Set[BaserowFunctionDefinition] = typed_expression.accept(
#             FunctionsUsedVisitor()
#         )
#         expression_needs_refresh_on_insert = any(
#             f.requires_refresh_after_insert for f in functions_used
#         )
#
#         new_formula_type = typed_expression.expression_type
#         new_formula_type.persist_onto_formula_field(updated_formula_field)
#         typed_field = TypedFieldWithReferences(
#             self.original_formula_field,
#             updated_formula_field,
#             typed_expression,
#             expression_needs_refresh_on_insert,
#         )
#
#         for field_child in self.field_children:
#             typed_field.add_child(field_name_to_typed_field[field_child])
#         for formula_child in self.formula_children.values():
#             typed_field.add_child(field_name_to_typed_field[formula_child.field_name])
#
#         return typed_field
#
#     def _create_untyped_copy_of_original_field(self):
#         updated_formula_field = deepcopy(self.original_formula_field)
#         for attr in BASEROW_FORMULA_TYPE_ALLOWED_FIELDS:
#             setattr(updated_formula_field, attr, None)
#         return updated_formula_field


# def _add_children_to_untyped_formula_raising_if_self_ref_found(
#     untyped_formula_field: UntypedFormulaFieldWithReferences,
#     field_name_to_untyped_formula: Dict[str, UntypedFormulaFieldWithReferences],
# ):
#     children = untyped_formula_field.untyped_expression.accept(
#         FieldReferenceResolvingVisitor()
#     )
#     for child in children:
#         if child in field_name_to_untyped_formula:
#             child_formula = field_name_to_untyped_formula[child]
#             untyped_formula_field.add_child_formulas_and_raise_if_self_ref_found(
#                 child_formula
#             )
#         else:
#             untyped_formula_field.add_child_field(child)
#
#
# def _find_formula_field_type_resolution_order_and_raise_if_circular_ref_found(
#     field_id_to_untyped_formula: Dict[str, UntypedFormulaFieldWithReferences]
# ) -> typing.OrderedDict[str, UntypedFormulaFieldWithReferences]:
#     ordered_untyped_formulas: OrderedDict[
#         str, UntypedFormulaFieldWithReferences
#     ] = OrderedDict()
#     for untyped_formula in field_id_to_untyped_formula.values():
#         untyped_formula.add_all_children_depth_first_order_raise_for_circular_ref(
#             OrderedDict(), ordered_untyped_formulas
#         )
#     return ordered_untyped_formulas


# def _calculate_non_formula_field_typed_expression(
#     field: Field,
# ):
#     field_type: FieldType = field_type_registry.get_by_model(field)
#     formula_type = field_type.to_baserow_formula_type(field)
#     typed_expr = BaserowFieldReference[BaserowFormulaValidType](
#         field.name, field.db_column, formula_type
#     )
#     return TypedFieldWithReferences(field, field, typed_expr, False)


# class TypedFieldWithReferences:
#     """
#     A wrapper graph node containing a field, it's typing information, references to it's
#     parents and child fields and it's original field instance before it was typed and
#     potentially changed.
#     """
#
#     def __init__(
#         self,
#         original_field: Field,
#         updated_field: Field,
#         typed_expression: BaserowExpression[BaserowFormulaType],
#         expression_needs_refresh_on_insert: bool,
#     ):
#         self.expression_needs_refresh_on_insert = expression_needs_refresh_on_insert
#         self.original_field = original_field
#         self.new_field = updated_field
#         self.typed_expression = typed_expression
#         self.children: Dict[str, "TypedFieldWithReferences"] = {}
#         self.parents: Dict[str, "TypedFieldWithReferences"] = {}
#
#     @property
#     def formula_type(self) -> BaserowFormulaType:
#         return self.typed_expression.expression_type
#
#     @property
#     def field_name(self) -> str:
#         return self.new_field.name
#
#     def add_all_missing_valid_parents(
#         self,
#         other_changed_fields: Dict[str, Field],
#         field_name_to_typed_field: Dict[str, "TypedFieldWithReferences"],
#     ):
#
#         for parent in self.parents.values():
#             typed_parent_field = field_name_to_typed_field[parent.field_name]
#             if typed_parent_field.formula_type.is_valid:
#                 typed_parent_field.add_all_missing_valid_parents(
#                     other_changed_fields, field_name_to_typed_field
#                 )
#                 other_changed_fields[parent.field_name] = typed_parent_field.new_field
#
#     def get_all_child_fields_not_already_found_recursively(
#         self, already_found_field_names: Set[str]
#     ) -> List[Field]:
#         all_not_found_already_child_fields = []
#         for child_field_id, child in self.children.items():
#             if child_field_id not in already_found_field_names:
#                 already_found_field_names.add(child_field_id)
#                 recursive_child_fields = (
#                     child.get_all_child_fields_not_already_found_recursively(
#                         already_found_field_names
#                     )
#                 )
#                 all_not_found_already_child_fields += [
#                     child.new_field
#                 ] + recursive_child_fields
#         return all_not_found_already_child_fields
#
#     def add_child(self, child: "TypedFieldWithReferences"):
#         self.children[child.field_name] = child
#         child.parents[self.field_name] = self


def _type_and_substitute_formula_field(
    formula_field: FormulaField,
    formula_field_node: FieldNode,
    field_name_to_typed_field_node: Dict[str, TypedFieldNode],
    update_graph: bool,
):
    untyped_expression = raw_formula_to_untyped_expression(formula_field.formula)
    typed_expr: BaserowExpression[BaserowFormulaType] = untyped_expression.accept(
        TypeAnnotatingASTVisitor(
            formula_field_node, field_name_to_typed_field_node, update_graph
        )
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

    return TypedFieldNode(wrapped_typed_expr, formula_field_node)


def type_and_update_formula_field(
    field: Field,
    raise_if_invalid: bool,
    recreate_field_if_needed: bool,
    fix_invalid_references: bool,
    update_graph: bool,
    field_name_to_typed_node: Optional[Dict[str, TypedFieldNode]] = None,
):
    update_needed = False
    if isinstance(field, FormulaField):
        formula_field = field
        typed_formula_field_node = type_formula_field(
            formula_field, field_name_to_typed_node
        )

        original = deepcopy(formula_field)
        expression = typed_formula_field_node.typed_expression
        expression_type = expression.expression_type

        if raise_if_invalid:
            expression_type.raise_if_invalid()

        expression_type.persist_onto_formula_field(formula_field)
        formula_field.internal_typed_formula = str(expression)

        if not original.same_as(formula_field):
            formula_field.save()
            ViewHandler().field_type_changed(formula_field)
            if recreate_field_if_needed:
                _recreate_field_if_required(
                    formula_field.table, original, expression_type, formula_field
                )

            update_needed = True

    if fix_invalid_references:
        try:
            if not hasattr(field, "fieldnode"):
                node = FieldNode.objects.create(field=field, table=field.table)
            else:
                node = field.fieldnode
            invalid_node_with_our_name = FieldNode.objects.get(
                table=field.table,
                field__isnull=True,
                unresolved_field_name=field.name,
            )
            new_children = FieldEdge.objects.filter(parent=invalid_node_with_our_name)
            new_children.update(parent=node)
            invalid_node_with_our_name.delete()
            update_needed = True
        except FieldNode.DoesNotExist:
            pass

    if update_needed:
        fields_needing_update = field.fieldnode.descendants(max_depth=1)
        for direct_descendant in fields_needing_update:
            type_and_update_formula_field(
                direct_descendant, False, True, False, field_name_to_typed_node
            )

    return typed_formula_field_node


def type_formula_field(
    formula_field: FormulaField,
    field_name_to_typed_node: Optional[Dict[str, TypedFieldNode]] = None,
):
    try:
        if hasattr(formula_field, "fieldnode"):
            node = formula_field.fieldnode
            # Delete all existing dependencies this formula_field has as we are about
            # to recreate them
            FieldEdge.objects.filter(child=formula_field.fieldnode).delete()
        else:
            node = FieldNode.objects.create(
                field=formula_field, table=formula_field.table
            )

        if field_name_to_typed_node is None:
            field_name_to_typed_node = {}
        typed_formula_field_node = _type_and_substitute_formula_field(
            formula_field, node, field_name_to_typed_node, True
        )
        return typed_formula_field_node
    except RecursionError:
        raise MaximumFormulaSizeError()


# def _parse_all_fields(
#     table: "models.Table",
# ):
#     all_fields, field_name_to_db_column = _get_all_fields_and_build_name_dict(
#         table, None
#     )
#
#     field_name_to_untyped_formula: Dict[str, UntypedFormulaFieldWithReferences] = {}
#     field_name_to_updated_typed_field: Dict[str, TypedFieldWithReferences] = {}
#
#     for field in all_fields:
#         specific_class = field.specific_class
#         field_type = field_type_registry.get_by_model(specific_class)
#         field_name = field.name
#         if field_type.type == "formula":
#             field_name_to_untyped_formula[
#                 field_name
#             ] = _parse_formula_string_to_untyped_expression(
#                 field, field_name_to_db_column
#             )
#         else:
#             updated_typed_field = _calculate_non_formula_field_typed_expression(field)
#             field_name_to_updated_typed_field[field_name] = updated_typed_field
#     return field_name_to_untyped_formula, field_name_to_updated_typed_field


class TypedBaserowTable:
    """
    Wrapper object class which contains the BaserowFormulaType types and inter field
    references for all fields in a table.
    """

    def __init__(
        self, table: "models.Table", typed_fields: Dict[str, TypedFieldWithReferences]
    ):
        self.table = table
        self.typed_fields_with_references = typed_fields

    def get_all_depended_on_fields(
        self, field: Field, field_names_to_ignore: Set[str]
    ) -> List[Field]:
        """
        Returns all other fields not already present in the field_ids_to_ignore set
        for which field depends on to calculate it's value.

        :param field: The field to get all dependant fields for.
        :param field_names_to_ignore: A set of field ids to ignore, will be updated with
            all the field id's of fields returned by this call.
        :return: A list of field instances for which field depends on.
        """

        if field.name not in self.typed_fields_with_references:
            return []
        typed_field = self.typed_fields_with_references[field.name]
        return typed_field.get_all_child_fields_not_already_found_recursively(
            field_names_to_ignore
        )

    def get_typed_field(self, field: Field) -> Optional[TypedFieldWithReferences]:
        """
        :param field: The field to get its typed expression for.
        :return: If the field has one it's BaserowExpression with type info otherwise
            None.
        """

        if field.name not in self.typed_fields_with_references:
            return None
        return self.typed_fields_with_references[field.name]

    def get_typed_field_instance(self, field_name: str) -> Field:
        """
        :param field_name: The field name get its newly typed field for.
        :return: The updated field instance after typing.
        """

        return self.typed_fields_with_references[field_name].new_field


def type_table(
    table: "models.Table", overridden_field: Optional[Field] = None
) -> TypedBaserowTable:
    """
    Given a table calculates all the Baserow Formula types for every non trashed
    field in that table.

    :param table: The table to type.
    :param overridden_field: An optional field instance which will be used instead of
        that field's current database value when typing the table.
    :return: A typed baserow table wrapper object containing type information for
        every field.
    """

    return TypedBaserowTable(type_fields(table, overridden_field=overridden_field))


class TypedBaserowTables:
    def __init__(self):
        self.typed_tables: Dict[int, TypedBaserowTable] = {}

    def add_table(self, typed_table: TypedBaserowTable):
        self.typed_tables[typed_table.table.id] = typed_table


def type_fields(
    fields: "List[models.Field]",
    overridden_field: Optional[Field] = None,
) -> TypedBaserowTables:
    """
    The key algorithm responsible for typing a set of fields in Baserow.

    :param fields: The table to find Baserow Formula Types for every field.
    :param overridden_field: An optional field instance which will be used instead of
        that field's current database value when typing the table.
    :return: A dictionary of field name to a wrapper object TypedFieldWithReferences
        containing type and reference information about that field.
    """
    pass
