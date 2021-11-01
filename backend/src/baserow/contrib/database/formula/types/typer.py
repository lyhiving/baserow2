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


class TypedField:
    def __init__(
        self,
        typed_expression: BaserowExpression[BaserowFormulaType],
        field,
    ):
        self.typed_expression = typed_expression
        self.field = field

    def name(self):
        return str(self.field.table.id) + "_" + self.field.name


class TypedBaserowFields:
    """
    A collection of Fields which have been typed. Some of the fields may need a values
    refresh due to a change in a dependant field which can be triggered by calling
    refresh_fields.
    """

    def __init__(self):
        self.typed_fields: Dict[str, TypedField] = {}
        self.fields_needing_values_refresh: List[TypedField] = []
        self.fields_needing_save: List[TypedField] = []

    def _unique_name_for_table_and_field_name(
        self, table: "models.Table", field_name: str
    ):
        return f"{str(table.id)}_{field_name}"

    def add_typed_field_node(self, typed_node: TypedField, values_refresh_needed=False):
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

    # _fix_invalid_refs(field)

    fields_needing_update = field.get_or_create_node().descendants(max_depth=1)
    for direct_descendant in fields_needing_update:
        type_and_update_field(
            direct_descendant.field.specific,
            already_typed_fields,
        )
    return already_typed_fields


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

        return TypedField(
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
    # Set field dependencies to

    return untyped_expression.accept(
        TypingAndGraphingVisitor(field_node, already_typed_fields, update_graph)
    )


class FieldReferenceExtractingVisitor(BaserowFormulaASTVisitor[UnTyped, List[str]]):
    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> List[str]:
        return [field_reference.referenced_field_name]

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[UnTyped]
    ) -> List[str]:
        return []

    def visit_function_call(
        self, function_call: BaserowFunctionCall[UnTyped]
    ) -> List[str]:
        field_references: List[str] = []
        for expr in function_call.args:
            field_references.append(expr.accept(self))
        return field_references

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral[UnTyped]
    ) -> List[str]:
        return []

    def visit_decimal_literal(
        self, decimal_literal: BaserowDecimalLiteral[UnTyped]
    ) -> List[str]:
        return []

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral[UnTyped]
    ) -> List[str]:
        return []


class TypingAndGraphingVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(
        self,
        field_node_being_typed,
        already_typed_fields: TypedBaserowFields,
    ):
        self.field_node_being_typed = field_node_being_typed
        self.already_typed_fields = already_typed_fields

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:

        typed_node = _calculate_expression_and_node_from_field_reference(
            self.field_node_being_typed.table,
            field_reference,
            self.already_typed_fields,
        )

        return typed_node.typed_expression

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
) -> TypedField:
    # TODO
    from baserow.contrib.database.fields.models import Field

    referenced_field_name = field_reference.referenced_field_name
    typed_field_node = already_typed_fields.get_field(table, referenced_field_name)

    if typed_field_node is None:
        try:
            typed_field_node = _lookup_expression_and_node_from_db(
                referenced_field_name, table
            )
        except Field.DoesNotExist:
            typed_field_node = _construct_broken_reference_node(
                field_reference, referenced_field_name, table
            )
        already_typed_fields.add_typed_field_node(typed_field_node)

    return typed_field_node


def _lookup_expression_and_node_from_db(referenced_field_name, table):
    from baserow.contrib.database.fields.registries import field_type_registry

    referenced_field = table.field_set.get(name=referenced_field_name).specific
    field_type = field_type_registry.get_by_model(referenced_field)
    expr = field_type.to_baserow_formula_expression(referenced_field)
    typed_field_node = TypedField(
        expr, referenced_field.get_or_create_node(), referenced_field
    )
    return typed_field_node
