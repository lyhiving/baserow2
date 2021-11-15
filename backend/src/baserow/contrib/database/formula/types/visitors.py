from typing import Any, Set, List

from baserow.contrib.database.fields.dependencies.exceptions import (
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.types import FieldDependencies
from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowStringLiteral,
    BaserowFieldReference,
    BaserowIntegerLiteral,
    BaserowDecimalLiteral,
    BaserowBooleanLiteral,
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.types.formula_type import (
    UnTyped,
    BaserowFormulaValidType,
)
from baserow.contrib.database.formula.types.formula_types import (
    BaserowExpression,
    BaserowFormulaType,
    BaserowFormulaTextType,
    BaserowFormulaNumberType,
    BaserowFormulaBooleanType,
)


class FunctionsUsedVisitor(
    BaserowFormulaASTVisitor[Any, Set[BaserowFunctionDefinition]]
):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return set()

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral
    ) -> Set[BaserowFunctionDefinition]:
        return set()

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral
    ) -> Set[BaserowFunctionDefinition]:
        return set()

    def visit_function_call(
        self, function_call: BaserowFunctionCall
    ) -> Set[BaserowFunctionDefinition]:
        all_used_functions = {function_call.function_def}
        for expr in function_call.args:
            all_used_functions.update(expr.accept(self))

        return all_used_functions

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral
    ) -> Set[BaserowFunctionDefinition]:
        return set()

    def visit_decimal_literal(
        self, decimal_literal: BaserowDecimalLiteral
    ) -> Set[BaserowFunctionDefinition]:
        return set()


class FieldReferenceExtractingVisitor(
    BaserowFormulaASTVisitor[UnTyped, FieldDependencies]
):
    """
    Calculates and returns all the field dependencies that the baserow expression has.
    """

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> FieldDependencies:
        return {field_reference.referenced_field_name}

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[UnTyped]
    ) -> FieldDependencies:
        return set()

    def visit_function_call(
        self, function_call: BaserowFunctionCall[UnTyped]
    ) -> FieldDependencies:
        field_references: FieldDependencies = set()
        for expr in function_call.args:
            field_references.update(expr.accept(self))
        return field_references

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral[UnTyped]
    ) -> FieldDependencies:
        return set()

    def visit_decimal_literal(
        self, decimal_literal: BaserowDecimalLiteral[UnTyped]
    ) -> FieldDependencies:
        return set()

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral[UnTyped]
    ) -> FieldDependencies:
        return set()


class FormulaTypingVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(self, field_being_typed, field_lookup_cache):
        self.field_lookup_cache = field_lookup_cache
        self.field_being_typed = field_being_typed

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        from baserow.contrib.database.fields.registries import field_type_registry

        referenced_field_name = field_reference.referenced_field_name
        if referenced_field_name == self.field_being_typed.name:
            raise SelfReferenceFieldDependencyError()

        table = self.field_being_typed.table
        referenced_field = self.field_lookup_cache.lookup_by_name(
            table, referenced_field_name
        )
        if referenced_field is None:
            return field_reference.with_invalid_type(
                f"references the deleted or unknown field"
                f" {field_reference.referenced_field_name}"
            )
        else:
            field_type = field_type_registry.get_by_model(referenced_field)
            return field_type.to_baserow_formula_expression(referenced_field)

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
