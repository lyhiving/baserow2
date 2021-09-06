from typing import Dict, Type

from django.db.models import Expression, Value, ExpressionWrapper, F, Field

from baserow.contrib.database.formula.ast.errors import UnknownFieldReference
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
    BaserowIntegerLiteral,
    BaserowFieldByIdReference,
    BaserowFieldReference,
)
from baserow.contrib.database.formula.ast.types import TypeResult
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError


def tree_to_django_expression(
    formula_tree: BaserowExpression, field_types, field_values, for_update
) -> Expression:
    try:
        return formula_tree.accept(
            BaserowFormulaToDjangoExpressionGenerator(
                field_types, field_values, for_update
            )
        )
    except RecursionError:
        raise MaximumFormulaSizeError()


class BaserowFormulaToDjangoExpressionGenerator(BaserowFormulaASTVisitor[Expression]):
    def __init__(
        self,
        field_types: Dict[int, TypeResult],
        model_instance,
        for_update: bool,
    ):
        self.model_instance = model_instance
        self.field_types = field_types
        self.for_update = for_update

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        raise UnknownFieldReference(field_reference.referenced_field_name)

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        field_id = field_by_id_reference.referenced_field_id
        db_field_name = f"field_{field_id}"
        if self.for_update:
            return ExpressionWrapper(
                F(db_field_name),
                output_field=self.field_types[field_id].resulting_field_type,
            )
        elif not hasattr(self.model_instance, db_field_name):
            raise UnknownFieldReference(field_id)
        else:
            return Value(
                getattr(self.model_instance, db_field_name),
                output_field=self.field_types[field_id].resulting_field_type,
            )

    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.function_def.to_django_expression(args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return Value(int_literal.literal)
