from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from baserow.contrib.database.formula.ast.function import BaserowFunctionDefinition
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFunctionCall,
)
from baserow.contrib.database.formula.parser.errors import (
    InvalidNumberOfArguments,
    BaserowFormulaSyntaxError,
)
from baserow.contrib.database.formula.parser.generated.BaserowFormula import (
    BaserowFormula,
)
from baserow.contrib.database.formula.parser.generated.BaserowFormulaLexer import (
    BaserowFormulaLexer,
)
from baserow.contrib.database.formula.parser.generated.BaserowFormulaVisitor import (
    BaserowFormulaVisitor,
)
from baserow.contrib.database.formula.registries import formula_function_registry


class BaserowFormulaErrorListener(ErrorListener):
    # noinspection PyPep8Naming
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        message = f"{offendingSymbol} line {line}, col {column}: {msg}"
        raise BaserowFormulaSyntaxError(message)


def raw_formula_to_tree(formula):
    lexer = BaserowFormulaLexer(InputStream(formula))
    stream = CommonTokenStream(lexer)
    parser = BaserowFormula(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(BaserowFormulaErrorListener())
    tree = parser.root()
    return BaserowFormulaToBaserowASTMapper().visit(tree)


class BaserowFormulaToBaserowASTMapper(BaserowFormulaVisitor):
    def visitRoot(self, ctx: BaserowFormula.RootContext):
        return ctx.expr().accept(self)

    def visitStringLiteral(self, ctx: BaserowFormula.StringLiteralContext):
        literal_without_outer_quotes = ctx.getText()[1:-1]
        if ctx.SINGLEQ_STRING_LITERAL() is not None:
            literal = literal_without_outer_quotes.replace("\\'", "'")
        else:
            literal = literal_without_outer_quotes.replace('\\"', '"')
        return BaserowStringLiteral(literal)

    def visitFunctionCall(self, ctx: BaserowFormula.FunctionCallContext):
        function_name = ctx.func_name().accept(self).lower()
        expr_children = ctx.expr()
        num_expressions = len(expr_children)
        function_def: BaserowFunctionDefinition = formula_function_registry.get(
            function_name
        )
        if not function_def.num_args.test(num_expressions):
            raise InvalidNumberOfArguments(function_def, num_expressions)
        args = [expr.accept(self) for expr in expr_children]
        return BaserowFunctionCall(function_def, args)

    def visitIndentifier(self, ctx: BaserowFormula.IndentifierContext):
        return ctx.getText()

    def visitFunc_name(self, ctx: BaserowFormula.Func_nameContext):
        return ctx.getText()

    def visitIdentifier(self, ctx: BaserowFormula.IdentifierContext):
        return ctx.getText()
