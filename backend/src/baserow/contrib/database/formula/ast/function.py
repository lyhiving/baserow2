import abc
from typing import List

from django.db.models import Expression

from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowExpression,
    UnTyped,
    BaserowFunctionDefinition,
    ArgCountSpecifier,
)
from baserow.contrib.database.formula.ast.type_types import ValidType, Typed


class FixedNumOfArgs(ArgCountSpecifier):
    def __str__(self):
        return f"exactly {self.count} arguments"

    def test(self, num_args):
        return self.count == num_args


class NumOfArgsGreaterThan(ArgCountSpecifier):
    def __str__(self):
        return f"more than {self.count} arguments"

    def test(self, num_args):
        return self.count < num_args


class OneArgumentBaserowFunction(BaserowFunctionDefinition):
    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[ValidType]],
        func_call: BaserowFunctionCall[UnTyped],
    ) -> BaserowExpression[Typed]:
        return self.type_function(func_call, args[0])

    @abc.abstractmethod
    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        pass

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return self.to_django_expression(args[0])

    @abc.abstractmethod
    def to_django_expression(self, arg: Expression) -> Expression:
        pass


class TwoArgumentBaserowFunction(BaserowFunctionDefinition):
    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[ValidType]],
        func_call: BaserowFunctionCall[UnTyped],
    ) -> BaserowExpression[Typed]:
        return self.type_function(func_call, args[0], args[1])

    @abc.abstractmethod
    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        pass

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return self.to_django_expression(args[0], args[1])

    @abc.abstractmethod
    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        pass
