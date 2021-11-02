from typing import List

from django.core.exceptions import ObjectDoesNotExist

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
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
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


def type_formula_field(
    formula_field,
):
    try:
        untyped_expression = raw_formula_to_untyped_expression(formula_field.formula)

        typed_expression = untyped_expression.accept(
            FormulaTypingVisitor(formula_field)
        )

        expression_type = typed_expression.expression_type
        merged_expression_type = (
            expression_type.new_type_with_user_and_calculated_options_merged(
                formula_field
            )
        )

        # Take into account any user set formatting options on this formula field.
        typed_expr_merged_with_user_options = typed_expression.with_type(
            merged_expression_type
        )

        wrapped_typed_expr = (
            typed_expr_merged_with_user_options.expression_type.wrap_at_field_level(
                typed_expr_merged_with_user_options
            )
        )

        return TypedField(wrapped_typed_expr, formula_field)
    except RecursionError:
        raise MaximumFormulaSizeError()


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


class FormulaTypingVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(
        self,
        field_being_typed,
    ):
        self.field_being_typed = field_being_typed

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:

        referenced_field_name = field_reference.referenced_field_name
        from baserow.contrib.database.fields.registries import field_type_registry

        try:
            referenced_field = self.field_being_typed.table.field_set.get(
                name=referenced_field_name
            ).specific
            field_type = field_type_registry.get_by_model(referenced_field)
            return field_type.to_baserow_formula_expression(referenced_field)
        except ObjectDoesNotExist:
            return field_reference.with_invalid_type(
                f"unknown field {field_reference.referenced_field_name}"
            )

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
