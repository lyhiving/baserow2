import abc
from typing import List, Type, Union, Callable, Any

from django.db.models import Expression

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    BaserowExpression,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
    BaserowSingleArgumentTypeChecker,
    BaserowArgumentTypeChecker,
)


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
    def arg_types(self) -> BaserowArgumentTypeChecker:
        return [self.arg_type]

    @property
    def arg_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        func_call: BaserowFunctionCall[UnTyped],
    ) -> BaserowExpression[BaserowFormulaType]:
        return self.type_function(func_call, args[0])

    @abc.abstractmethod
    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        pass

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return self.to_django_expression(args[0])

    @abc.abstractmethod
    def to_django_expression(self, arg: Expression) -> Expression:
        pass

    def call_and_type_with(
        self, arg: BaserowExpression[BaserowFormulaType]
    ) -> BaserowFunctionCall[BaserowFormulaType]:
        return self.call_and_type_with_args([arg])


class TwoArgumentBaserowFunction(BaserowFunctionDefinition):
    @property
    def arg_types(self) -> BaserowArgumentTypeChecker:
        return [self.arg1_type, self.arg2_type]

    @property
    def arg1_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def arg2_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        func_call: BaserowFunctionCall[UnTyped],
    ) -> BaserowExpression[BaserowFormulaType]:
        return self.type_function(func_call, args[0], args[1])

    @abc.abstractmethod
    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        pass

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return self.to_django_expression(args[0], args[1])

    @abc.abstractmethod
    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        pass

    def call_and_type_with(
        self,
        arg1: BaserowExpression[BaserowFormulaType],
        arg2: BaserowExpression[BaserowFormulaType],
    ) -> BaserowFunctionCall[BaserowFormulaType]:
        return self.call_and_type_with_args([arg1, arg2])


class ThreeArgumentBaserowFunction(BaserowFunctionDefinition):
    @property
    def arg_types(self) -> BaserowArgumentTypeChecker:
        return [self.arg1_type, self.arg2_type, self.arg3_type]

    @property
    def arg1_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def arg2_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def arg3_type(self) -> BaserowSingleArgumentTypeChecker:
        return [BaserowFormulaValidType]

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(3)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        func_call: BaserowFunctionCall[UnTyped],
    ) -> BaserowExpression[BaserowFormulaType]:
        return self.type_function(func_call, args[0], args[1], args[2])

    @abc.abstractmethod
    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
        arg3: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        pass

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return self.to_django_expression(args[0], args[1], args[2])

    @abc.abstractmethod
    def to_django_expression(
        self, arg1: Expression, arg2: Expression, arg3: Expression
    ) -> Expression:
        pass

    def call_and_type_with(
        self,
        arg1: BaserowExpression[BaserowFormulaType],
        arg2: BaserowExpression[BaserowFormulaType],
        arg3: BaserowExpression[BaserowFormulaType],
    ) -> BaserowFunctionCall[BaserowFormulaType]:
        return self.call_and_type_with_args([arg1, arg2, arg3])
