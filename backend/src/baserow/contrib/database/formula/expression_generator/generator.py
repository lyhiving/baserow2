from typing import Dict

from django.db import models
from django.db.models import (
    Expression,
    Value,
    ExpressionWrapper,
    F,
    Field,
    DecimalField,
)

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
from baserow.contrib.database.formula.ast.type_types import Typed, InvalidType
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError


def tree_to_django_expression(
    formula_tree: BaserowExpression[Typed], model_instance, for_update
) -> Expression:
    try:
        if isinstance(formula_tree.expression_type, InvalidType):
            return Value(None)
        else:
            return formula_tree.accept(
                BaserowExpressionToDjangoExpressionGenerator(model_instance, for_update)
            )
    except RecursionError:
        raise MaximumFormulaSizeError()


class BaserowExpressionToDjangoExpressionGenerator(
    BaserowFormulaASTVisitor[Field, Expression]
):
    def __init__(
        self,
        model_instance,
        for_update: bool,
    ):
        self.model_instance = model_instance
        self.for_update = for_update

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        raise UnknownFieldReference(field_reference.referenced_field_name)

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        field_id = field_by_id_reference.referenced_field_id
        db_field_name = f"field_{field_id}"
        if self.for_update:
            return F(db_field_name)
        elif not hasattr(self.model_instance, db_field_name):
            raise UnknownFieldReference(field_id)
        else:
            return Value(
                getattr(self.model_instance, db_field_name),
            )

    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.to_django_expression_given_args(args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal, output_field=models.TextField())

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return Value(
            int_literal.literal,
            output_field=DecimalField(max_digits=50, decimal_places=0),
        )
