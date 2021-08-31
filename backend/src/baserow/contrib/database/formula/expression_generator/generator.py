from django.db.models import Expression, Value

from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
    BaserowIntegerLiteral,
)


def tree_to_django_expression(formula_tree: BaserowExpression) -> Expression:
    return formula_tree.accept(BaserowFormulaToDjangoExpressionGenerator())


class BaserowFormulaToDjangoExpressionGenerator(BaserowFormulaASTVisitor[Expression]):
    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.function_def.to_django_expression(args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return Value(int_literal.literal)
