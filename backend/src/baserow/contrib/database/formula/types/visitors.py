from typing import Any, Set, List

from baserow.contrib.database.fields.dependencies.exceptions import (
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies import handler as dep_handler
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
    BaserowFormulaASTVisitor[UnTyped, "dep_handler.FieldDependencies"]
):
    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        if field_reference.referenced_lookup_field is None:
            return [field_reference.referenced_field_name]
        else:
            return [
                (
                    field_reference.referenced_field_name,
                    field_reference.referenced_lookup_field,
                )
            ]

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        return []

    def visit_function_call(
        self, function_call: BaserowFunctionCall[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        field_references: "dep_handler.FieldDependencies" = []
        for expr in function_call.args:
            field_references += expr.accept(self)
        return field_references

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        return []

    def visit_decimal_literal(
        self, decimal_literal: BaserowDecimalLiteral[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        return []

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral[UnTyped]
    ) -> "dep_handler.FieldDependencies":
        return []


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
        referenced_field = self.field_lookup_cache.lookup(table, referenced_field_name)
        if referenced_field is None:
            return field_reference.with_invalid_type(
                f"references the deleted or unknown field"
                f" {field_reference.referenced_field_name}"
            )
        else:
            field_type = field_type_registry.get_by_model(referenced_field)
            lookup_field = field_reference.referenced_lookup_field
            if lookup_field is not None:
                from baserow.contrib.database.fields.models import LinkRowField

                if not isinstance(referenced_field, LinkRowField):
                    return field_reference.with_invalid_type(
                        "first lookup function argument must be a link row field"
                    )
                target_table = referenced_field.link_row_table

                lookup_field = self.field_lookup_cache.lookup(
                    target_table, lookup_field
                )
                if lookup_field is None:
                    return field_reference.with_invalid_type(
                        f"references the deleted or unknown lookup field"
                        f" {field_reference.referenced_lookup_field} in table "
                        f"{target_table.name}"
                    )
                else:
                    lookup_field_type = field_type_registry.get_by_model(lookup_field)
                    formula_type = lookup_field_type.to_baserow_formula_type(
                        lookup_field
                    )
                    return BaserowFieldReference(
                        referenced_field.db_column, lookup_field.db_column, formula_type
                    )
            # check the lookup field
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
