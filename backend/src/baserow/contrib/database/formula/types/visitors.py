from typing import Any, List, Set

from django.conf import settings

from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowStringLiteral,
    BaserowFieldReference,
    BaserowIntegerLiteral,
    BaserowExpression,
    BaserowDecimalLiteral,
    BaserowBooleanLiteral,
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.types.exceptions import (
    NoSelfReferencesError,
    NoCircularReferencesError,
)
from baserow.contrib.database.formula.types.formula_type import (
    UnTyped,
    BaserowFormulaType,
    BaserowFormulaValidType,
)
from baserow.contrib.database.formula.types.formula_types import (
    BaserowFormulaTextType,
    BaserowFormulaNumberType,
    BaserowFormulaBooleanType,
)
from baserow.contrib.database.formula.types.util import (
    _lookup_underlying_field_from_reference,
)


class FieldReferenceResolvingVisitor(
    BaserowFormulaASTVisitor[Any, List[BaserowFieldReference]]
):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return [field_reference]

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> List[str]:
        return []

    def visit_boolean_literal(
        self, boolean_literal: BaserowBooleanLiteral
    ) -> List[str]:
        return []

    def visit_function_call(self, function_call: BaserowFunctionCall) -> List[str]:
        all_arg_references = []
        for expr in function_call.args:
            all_arg_references += expr.accept(self)

        return all_arg_references

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return []

    def visit_decimal_literal(self, decimal_literal: BaserowDecimalLiteral):
        return []


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


class TypeAnnotatingASTVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(self, field_node, already_typed_fields, update_graph=True):
        self.field_node = field_node
        self.already_typed_fields = already_typed_fields
        self.update_graph = update_graph

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        unique_name = (
            str(self.field_node.table_id) + "_" + field_reference.referenced_field_name
        )
        if self.field_node.field.name == field_reference.referenced_field_name:
            raise NoSelfReferencesError()
        if self.already_typed_fields.has(unique_name):
            typed_node = self.already_typed_fields.get(unique_name)
        else:
            typed_node = _lookup_underlying_field_from_reference(
                self.field_node,
                field_reference,
                self.already_typed_fields,
            )
            self.already_typed_fields.add_node(typed_node)
        if self.update_graph:
            if self.field_node not in typed_node.field_node.self_and_ancestors(
                max_depth=settings.MAX_FIELD_REFERENCE_DEPTH
            ):
                typed_node.field_node.add_child(
                    self.field_node, disable_circular_check=True
                )
            else:
                raise NoCircularReferencesError()
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
