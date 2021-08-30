from typing import Dict, Type

from django.db.models import Expression, Func, Value
from django.db.models.functions import Upper, Lower, Concat

from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.ast.function_defs import (
    BaserowUpper,
    BaserowLower,
    BaserowConcat,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
)
from baserow.contrib.database.formula.expression_generator.errors import (
    UnknownBaserowFunction,
)


def tree_to_django_expression(formula_tree: BaserowExpression) -> Expression:
    return formula_tree.accept(BaserowFormulaToDjangoExpressionGenerator())


BASEROW_FORMULA_FUNCTION_TO_DJANGO_EXPRESSION: Dict[str, Type[Func]] = {
    BaserowUpper.type: Upper,
    BaserowLower.type: Lower,
    BaserowConcat.type: Concat,
}


def map_baserow_to_django_expression(
    function_def: BaserowFunctionDefinition,
) -> Type[Func]:
    if function_def.type not in BASEROW_FORMULA_FUNCTION_TO_DJANGO_EXPRESSION:
        raise UnknownBaserowFunction(function_def)

    return BASEROW_FORMULA_FUNCTION_TO_DJANGO_EXPRESSION[function_def.type]


class BaserowFormulaToDjangoExpressionGenerator(BaserowFormulaASTVisitor[Expression]):
    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]

        django_expression_func = map_baserow_to_django_expression(
            function_call.function_def
        )
        return django_expression_func(*args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal)
