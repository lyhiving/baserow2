from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from baserow.contrib.database.formula.ast.errors import UnknownFieldReference
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowExpression,
    BaserowIntegerLiteral,
    BaserowFieldReference,
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
from baserow.core.exceptions import InstanceTypeDoesNotExist


class BaserowFormulaErrorListener(ErrorListener):
    # noinspection PyPep8Naming
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        msg = msg.replace("<EOF>", "the end of the formula")
        message = f"Invalid syntax at line {line}, col {column}: {msg}"
        raise BaserowFormulaSyntaxError(message)


def raw_formula_to_tree(formula: str, field_db_names) -> BaserowExpression:
    lexer = BaserowFormulaLexer(InputStream(formula))
    stream = CommonTokenStream(lexer)
    parser = BaserowFormula(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(BaserowFormulaErrorListener())
    tree = parser.root()
    # need to save name -> field_1
    return BaserowFormulaToBaserowASTMapper(field_db_names).visit(tree)


class BaserowFormulaToBaserowASTMapper(BaserowFormulaVisitor):
    def __init__(self, field_db_names):
        self.field_db_names = field_db_names

    def visitRoot(self, ctx: BaserowFormula.RootContext):
        return ctx.expr().accept(self)

    def visitStringLiteral(self, ctx: BaserowFormula.StringLiteralContext):
        literal = self.process_string(ctx)
        return BaserowStringLiteral(literal)

    def process_string(self, ctx):
        literal_without_outer_quotes = ctx.getText()[1:-1]
        if ctx.SINGLEQ_STRING_LITERAL() is not None:
            literal = literal_without_outer_quotes.replace("\\'", "'")
        else:
            literal = literal_without_outer_quotes.replace('\\"', '"')
        return literal

    def visitFunctionCall(self, ctx: BaserowFormula.FunctionCallContext):
        function_name = ctx.func_name().accept(self).lower()
        function_argument_expressions = ctx.expr()

        return self._do_func(function_argument_expressions, function_name)

    def _do_func(self, function_argument_expressions, function_name):
        function_def = self._get_function_def(function_name)
        self._check_function_call_valid(function_argument_expressions, function_def)
        args = [expr.accept(self) for expr in function_argument_expressions]
        return BaserowFunctionCall(function_def, args)

    def visitBinaryOp(self, ctx: BaserowFormula.BinaryOpContext):
        op = "add" if ctx.PLUS() else "minus"

        return self._do_func(ctx.expr(), op)

    @staticmethod
    def _check_function_call_valid(function_argument_expressions, function_def):
        num_expressions = len(function_argument_expressions)
        if not function_def.num_args.test(num_expressions):
            raise InvalidNumberOfArguments(function_def, num_expressions)

    @staticmethod
    def _get_function_def(function_name):
        try:
            function_def = formula_function_registry.get(function_name)
        except InstanceTypeDoesNotExist:
            raise BaserowFormulaSyntaxError(f"{function_name} is not a valid function")
        return function_def

    def visitFunc_name(self, ctx: BaserowFormula.Func_nameContext):
        return ctx.getText()

    def visitIdentifier(self, ctx: BaserowFormula.IdentifierContext):
        return ctx.getText()

    def visitIntegerLiteral(self, ctx: BaserowFormula.IntegerLiteralContext):
        return BaserowIntegerLiteral(int(ctx.getText()))

    def visitFieldReference(self, ctx: BaserowFormula.FieldReferenceContext):
        field_name = self.process_string(ctx.field_reference())
        if field_name not in self.field_db_names:
            raise UnknownFieldReference(field_name)
        return BaserowFieldReference(self.field_db_names[field_name])
