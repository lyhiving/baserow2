from django.db.models import Expression, Value

from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
)


def tree_to_django_expression(formula_tree: BaserowExpression) -> Expression:
    return formula_tree.accept(BaserowFormulaToDjangoExpressionGenerator())


class BaserowFormulaToDjangoExpressionGenerator(BaserowFormulaASTVisitor[Expression]):
    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]

        django_expression_func = function_call.function_def.to_django_function()
        return django_expression_func(*args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal)
