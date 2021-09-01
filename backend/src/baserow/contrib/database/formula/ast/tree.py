import abc
from typing import List, TypeVar, Generic

from django.conf import settings

from baserow.contrib.database.formula.ast.errors import (
    InvalidStringLiteralProvided,
    TooLargeStringLiteralProvided,
    InvalidIntLiteralProvided,
)


class BaserowExpression(abc.ABC):
    @abc.abstractmethod
    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        pass


class BaserowStringLiteral(BaserowExpression):
    def __init__(self, literal: str):
        if not isinstance(literal, str):
            raise InvalidStringLiteralProvided()
        if len(literal) > settings.MAX_FORMULA_STRING_LENGTH:
            raise TooLargeStringLiteralProvided()
        self.literal = literal

    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_string_literal(self)

    def __str__(self):
        return self.literal


class BaserowIntegerLiteral(BaserowExpression):
    def __init__(self, literal: int):
        if not isinstance(literal, int):
            raise InvalidIntLiteralProvided()
        self.literal = literal

    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_int_literal(self)

    def __str__(self):
        return str(self.literal)


class BaserowFunctionCall(BaserowExpression):
    def __init__(self, function_def, args: List[BaserowExpression]):
        self.function_def = function_def
        self.args = args

    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_function_call(self)

    def __str__(self):
        return f"{self.function_def.type}({','.join([str(a) for a in self.args])})"


class BaserowFieldReference(BaserowExpression):
    def accept(self, visitor: "BaserowFormulaASTVisitor"):
        return visitor.visit_field_reference(self)

    def __init__(self, referenced_field: str):
        self.referenced_field = referenced_field

    def __str__(self):
        return f"field({self.referenced_field})"


T = TypeVar("T")


class BaserowFormulaASTVisitor(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> T:
        pass

    @abc.abstractmethod
    def visit_function_call(self, function_call: BaserowFunctionCall) -> T:
        pass

    @abc.abstractmethod
    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        pass

    @abc.abstractmethod
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        pass
