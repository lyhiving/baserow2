from typing import Dict, Type

from django.db.models import Expression, Value, ExpressionWrapper, F, Field

from baserow.contrib.database.formula.ast.errors import UnknownFieldReference
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
    BaserowIntegerLiteral,
    BaserowFieldReference,
)
from baserow.contrib.database.formula.ast.types import TypeResult


def tree_to_django_expression(
    formula_tree: BaserowExpression, field_types, field_values, for_update
) -> Expression:
    return formula_tree.accept(
        BaserowFormulaToDjangoExpressionGenerator(field_types, field_values, for_update)
    )


class BaserowFormulaToDjangoExpressionGenerator(BaserowFormulaASTVisitor[Expression]):
    def __init__(
        self,
        field_types: Dict[str, TypeResult],
        field_values: Dict[str, Expression],
        for_update: bool,
    ):
        self.field_values = field_values
        self.field_types = field_types
        self.for_update = for_update

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        if self.for_update:
            return ExpressionWrapper(
                F(field_reference.referenced_field),
                output_field=self.field_types[
                    field_reference.referenced_field
                ].resulting_field_type,
            )
        elif not hasattr(self.field_values, field_reference.referenced_field):
            raise UnknownFieldReference(field_reference.referenced_field)
        else:
            return Value(
                getattr(self.field_values, field_reference.referenced_field),
                output_field=self.field_types[
                    field_reference.referenced_field
                ].resulting_field_type,
            )

    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.function_def.to_django_expression(args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return Value(int_literal.literal)
