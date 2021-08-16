from baserow.contrib.database.formula.ast.function import (
    StandardFunction,
    InlineOperator,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
)
from baserow.contrib.database.formula.generated_column_generator.errors import (
    UnknownFunctionDefinitionType,
)


def tree_to_generated_column_sql(formula_tree):
    return formula_tree.accept(BaserowFormulaToGeneratedColumnGenerator())


class BaserowFormulaToGeneratedColumnGenerator(BaserowFormulaASTVisitor):
    def visit_function_call(self, function_call: BaserowFunctionCall):
        args = [expr.accept(self) for expr in function_call.args]

        function_def = function_call.function_def
        function_type = function_def.sql_function

        if isinstance(function_type, StandardFunction):
            return f"{function_type.name}({','.join(args)})"
        elif isinstance(function_type, InlineOperator):
            return function_type.name.join(args)
        else:
            raise UnknownFunctionDefinitionType(function_type)

    def visit_string_literal(self, string_literal: BaserowStringLiteral):
        escaped_literal = string_literal.literal.replace("'", "\\'")
        return f"'{escaped_literal}'"
