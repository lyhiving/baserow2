import abc
from typing import Dict

from psycopg2.extensions import adapt

from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.ast.function_defs import Upper, Lower, Concat
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
)
from baserow.contrib.database.formula.generated_column_generator.errors import (
    UnknownFunctionDefinitionType,
    UnknownBaserowFunction,
)


def tree_to_generated_column_sql(formula_tree: BaserowExpression) -> str:
    return formula_tree.accept(BaserowFormulaToGeneratedColumnGenerator())


class PostgresFunctionTypeSpecifier(abc.ABC):
    """
    An abstract base class used to specify the various ways a function should work.
    """

    def __init__(self, name):
        self.name = name


class StandardPostgresFunction(PostgresFunctionTypeSpecifier):
    pass


class PostgresInlineOperator(PostgresFunctionTypeSpecifier):
    pass


BASEROW_FORMULA_FUNCTION_TO_POSTGRES_FUNCTION: Dict[
    str,
    PostgresFunctionTypeSpecifier,
] = {
    Upper.type: StandardPostgresFunction("UPPER"),
    Lower.type: StandardPostgresFunction("LOWER"),
    Concat.type: PostgresInlineOperator("||"),
}


def map_baserow_to_postgres_function(
    function_def: BaserowFunctionDefinition,
) -> PostgresFunctionTypeSpecifier:
    if function_def.type not in BASEROW_FORMULA_FUNCTION_TO_POSTGRES_FUNCTION:
        raise UnknownBaserowFunction(function_def)

    return BASEROW_FORMULA_FUNCTION_TO_POSTGRES_FUNCTION[function_def.type]


class BaserowFormulaToGeneratedColumnGenerator(BaserowFormulaASTVisitor[str]):
    def visit_function_call(self, function_call: BaserowFunctionCall) -> str:
        args = [expr.accept(self) for expr in function_call.args]

        psql_function = map_baserow_to_postgres_function(function_call.function_def)

        if isinstance(psql_function, StandardPostgresFunction):
            return f"{psql_function.name}({','.join(args)})"
        elif isinstance(psql_function, PostgresInlineOperator):
            return psql_function.name.join(args)
        else:
            raise UnknownFunctionDefinitionType(psql_function)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> str:
        # noinspection PyArgumentList
        encoded = adapt(string_literal.literal)
        # We don't have a psycopg2 connection here the adapt function can use to get
        # the encoding, so it defaults to latin-1. Django by default uses utf-8
        # connections to postgres so we set it here to ensure we don't get any
        # encoding errors.
        encoded.encoding = "utf-8"
        return str(encoded)
