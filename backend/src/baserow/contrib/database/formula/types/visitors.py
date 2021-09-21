from typing import Any, List, Dict

from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowStringLiteral,
    BaserowFieldReference,
    BaserowIntegerLiteral,
    BaserowFieldByIdReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.types.type_defs import (
    BaserowFormulaTextType,
    BaserowFormulaNumberType,
)
from baserow.contrib.database.formula.types.type_types import (
    UnTyped,
    BaserowFormulaType,
    BaserowFormulaValidType,
)


class FieldReferenceResolvingVisitor(BaserowFormulaASTVisitor[Any, List[str]]):
    def visit_field_reference(self, field_reference: BaserowFunctionCall):
        # The only time when we should encounter a field reference here is when this
        # field is pointing at a trashed or deleted field.
        return []

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> List[str]:
        return []

    def visit_function_call(self, function_call: BaserowFunctionCall) -> List[str]:
        all_arg_references = [expr.accept(self) for expr in function_call.args]
        combined_references = []
        for arg_references in all_arg_references:
            combined_references += arg_references

        return combined_references

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return []

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        return [field_by_id_reference.referenced_field_id]


class TypeAnnotatingASTVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(self, field_id_to_type):
        self.field_id_to_type: Dict[
            int, BaserowExpression[BaserowFormulaType]
        ] = field_id_to_type

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return field_reference.with_invalid_type(
            f"references the deleted field {field_reference.referenced_field_name}"
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

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        field_id = field_by_id_reference.referenced_field_id
        if field_id in self.field_id_to_type:
            return self.field_id_to_type[field_by_id_reference.referenced_field_id]
        else:
            return field_by_id_reference.with_invalid_type(
                f"references an unknown field with id "
                f"{field_by_id_reference.referenced_field_id}"
            )


class SubstituteFieldByIdWithThatFieldsExpressionVisitor(
    BaserowFormulaASTVisitor[Any, BaserowExpression]
):
    def visit_field_reference(self, field_reference: BaserowFieldByIdReference):
        return field_reference

    def __init__(self, field_id_to_expression: Dict[int, BaserowExpression]):
        self.field_id_to_expression = field_id_to_expression

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral
    ) -> BaserowExpression:
        return string_literal

    def visit_function_call(
        self, function_call: BaserowFunctionCall
    ) -> BaserowExpression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.with_args(args)

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral
    ) -> BaserowExpression:
        return int_literal

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ) -> BaserowExpression:
        if field_by_id_reference.referenced_field_id in self.field_id_to_expression:
            return self.field_id_to_expression[
                field_by_id_reference.referenced_field_id
            ]
        else:
            return field_by_id_reference
