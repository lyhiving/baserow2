from typing import Any, List, Dict, Set, Optional

from django.core.exceptions import ValidationError

from baserow.contrib.database.fields.models import FieldNode, Field, FormulaField
from baserow.contrib.database.fields.registries import field_type_registry
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
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.types import typer
from baserow.contrib.database.formula.types.exceptions import NoCircularReferencesError
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
from baserow.contrib.database.formula.types.typer import (
    TypedFieldNode,
    type_formula_field,
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


def _lookup_underlying_field_from_reference(
    formula_field_node: FieldNode,
    field_reference: BaserowFieldReference,
    update_graph=True,
    field_name_to_typed_node: Optional[Dict[str, TypedFieldNode]] = None,
) -> TypedFieldNode:
    table = formula_field_node.field.table
    try:
        referenced_field = table.field_set.get(
            name=field_reference.referenced_field_name
        ).specific
        field_type = field_type_registry.get_by_model(referenced_field)
        formula_type = field_type.to_baserow_formula_type(referenced_field)
        if isinstance(referenced_field, FormulaField):
            if referenced_field.internal_typed_formula is not None:
                expr = raw_formula_to_untyped_expression(
                    referenced_field.internal_typed_formula
                ).with_type(formula_type)
            else:
                typed_node = type_formula_field(
                    referenced_field, field_name_to_typed_node
                )
                expr = typed_node.typed_expression
                referenced_field.internal_typed_formula = str(expr)
                referenced_field.save()

        else:
            expr = field_reference.with_type(formula_type)
        typed_field_node = TypedFieldNode(
            expr,
            FieldNode.objects.get_or_create(
                field=referenced_field, defaults={table: referenced_field.table}
            ),
        )
    except Field.DoesNotExist:
        typed_field_node = TypedFieldNode(
            field_reference.with_invalid_type(
                f"Unknown or deleted field called "
                f"{field_reference.referenced_field_name} referenced"
            ),
            FieldNode.objects.get_or_create(
                table=table, unresolved_field_name=field_reference.referenced_field_name
            ),
        )
    if update_graph:
        try:
            # TODO MAX DEPTH
            typed_field_node.field_node.add_child(formula_field_node)
        except ValidationError:
            raise NoCircularReferencesError()
    return typed_field_node


class TypeAnnotatingASTVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(self, field_node, field_name_to_typed_field_node, update_graph=True):
        self.field_node = field_node
        self.field_to_typed_node: Dict[
            str, "typer.TypedFieldNode"
        ] = field_name_to_typed_field_node
        self.update_graph = update_graph

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        unique_name = (
            str(self.field_node.table_id) + "_" + field_reference.referenced_field_name
        )
        if unique_name in self.field_to_typed_node:
            typed_node = self.field_to_typed_node[unique_name]
        else:
            typed_node = _lookup_underlying_field_from_reference(
                self.field_node, field_reference, update_graph=self.update_graph
            )
            self.field_to_typed_node[unique_name] = typed_node
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


class SubstituteFieldWithThatFieldsExpressionVisitor(
    BaserowFormulaASTVisitor[Any, BaserowExpression]
):
    def __init__(
        self,
        field_name_to_typed_field: Dict[str, "typer.TypedFieldWithReferences"],
    ):
        self.field_name_to_typed_field = field_name_to_typed_field

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        field_name = field_reference.referenced_field_name
        if field_name in self.field_name_to_typed_field:
            typed_field = self.field_name_to_typed_field[field_name]
            return typed_field.typed_expression
        else:
            return field_reference

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

    def visit_decimal_literal(self, decimal_literal: BaserowDecimalLiteral):
        return decimal_literal

    def visit_boolean_literal(self, boolean_literal: BaserowBooleanLiteral):
        return boolean_literal
