import abc
from typing import Generic, TypeVar

from baserow.contrib.database.formula.ast.tree import BaserowStringLiteral, \
    BaserowFunctionCall, BaserowIntegerLiteral, BaserowFieldByIdReference, \
    BaserowFieldReference

Y = TypeVar("Y")
X = TypeVar("X")


class BaserowFormulaASTVisitor(abc.ABC, Generic[Y, X]):
    @abc.abstractmethod
    def visit_string_literal(self, string_literal: BaserowStringLiteral[Y]) -> X:
        pass

    @abc.abstractmethod
    def visit_function_call(self, function_call: BaserowFunctionCall[Y]) -> X:
        pass

    @abc.abstractmethod
    def visit_int_literal(self, int_literal: BaserowIntegerLiteral[Y]) -> X:
        pass

    @abc.abstractmethod
    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference[Y]
    ) -> X:
        pass

    @abc.abstractmethod
    def visit_field_reference(self, field_reference: BaserowFieldReference[Y]) -> X:
        pass