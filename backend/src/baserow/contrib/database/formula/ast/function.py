import abc
from typing import List, Type, Union, Callable, Any

from django.db.models import Expression

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    BaserowExpression,
    BaserowArgumentTypeChecker,
    BaserowSingleArgumentTypeChecker,
)
from baserow.contrib.database.formula.ast.type_types import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
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
        return self.call_and_type_with_valid_args([arg])


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
        return self.call_and_type_with_valid_args([arg1, arg2])


class ThreeArgumentBaserowFunction(BaserowFunctionDefinition):
    @property
    def arg_types(self) -> List[List[Type[BaserowFormulaValidType]]]:
        return [self.arg1_type, self.arg2_type, self.arg3_type]

    @abc.abstractmethod
    @property
    def arg1_type(self) -> List[Type[BaserowFormulaValidType]]:
        pass

    @abc.abstractmethod
    @property
    def arg2_type(self) -> List[Type[BaserowFormulaValidType]]:
        pass

    @abc.abstractmethod
    @property
    def arg3_type(self) -> List[Type[BaserowFormulaValidType]]:
        pass

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


def check_arg_type(
    expr_being_typed: BaserowExpression[UnTyped],
    arg_to_type_check: BaserowExpression[BaserowFormulaValidType],
    valid_arg_types: List[Type[Field]],
    resulting_type_if_valid: BaserowFormulaValidType,
) -> BaserowExpression[BaserowFormulaType]:
    for valid_arg_type in valid_arg_types:
        arg_type = arg_to_type_check.expression_type
        if isinstance(arg_type, valid_arg_type):
            return expr_being_typed.with_valid_type(resulting_type_if_valid)
    valid_types_str = ",".join([str(t) for t in valid_arg_types])
    return expr_being_typed.with_invalid_type(
        f"must be one of {valid_types_str} but was instead {type(arg_to_type_check)}"
    )


def check_types(
    func_being_typed: BaserowFunctionCall[UnTyped],
    args_to_type_check: List[BaserowExpression[BaserowFormulaValidType]],
    valid_arg_types: List[Type[BaserowFormulaValidType]],
    resulting_func_type_if_valid: Union[
        BaserowFormulaValidType, Callable[[List[Any]], BaserowFormulaValidType]
    ],
) -> BaserowExpression[BaserowFormulaType]:
    invalid_types = []
    valid_types = []
    for i, arg_to_type_check in enumerate(args_to_type_check):
        matching_type_found = False
        arg_type = arg_to_type_check.expression_type
        for valid_arg_type in valid_arg_types:
            if isinstance(arg_type, valid_arg_type):
                matching_type_found = True
                break
        if matching_type_found:
            valid_types.append(arg_type)
        else:
            invalid_types.append((i, arg_type))
    if len(invalid_types) > 0:
        error = ",".join(
            [f"argument {i} invalid as it was a {type(r)}" for i, r in invalid_types]
        )
        return func_being_typed.with_invalid_type(error)
    else:
        if callable(resulting_func_type_if_valid):
            resulting_func_type_if_valid = resulting_func_type_if_valid(valid_types)
        return func_being_typed.with_valid_type(resulting_func_type_if_valid)
