import abc
from typing import List

from baserow.contrib.database.formula.ast.errors import InvalidStringLiteralProvided
from baserow.contrib.database.formula.ast.function import BaserowFunctionDefinition


class BaserowExpression(abc.ABC):
    @abc.abstractmethod
    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        pass


class BaserowStringLiteral(BaserowExpression):
    def __init__(self, literal: str):
        if not isinstance(literal, str):
            raise InvalidStringLiteralProvided()
        self.literal = literal

    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_string_literal(self)


class BaserowFunctionCall(BaserowExpression):
    def __init__(
        self, function_def: BaserowFunctionDefinition, args: List[BaserowExpression]
    ):
        self.function_def = function_def
        self.args = args

    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_function_call(self)


class BaserowFormulaASTVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_string_literal(self, string_literal: BaserowStringLiteral):
        pass

    @abc.abstractmethod
    def visit_function_call(self, function_call: BaserowFunctionCall):
        pass
