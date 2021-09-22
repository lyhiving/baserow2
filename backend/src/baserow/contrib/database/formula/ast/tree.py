import abc
from typing import List, TypeVar, Generic, Tuple

from django.conf import settings
from django.db.models import Expression

from baserow.contrib.database.formula.ast import visitors
from baserow.contrib.database.formula.ast.errors import (
    InvalidStringLiteralProvided,
    TooLargeStringLiteralProvided,
    InvalidIntLiteralProvided,
)
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.formula.types import type_types
from baserow.core.registry import Instance

A = TypeVar("A")
T = TypeVar("T")
R = TypeVar("R")


class BaserowExpression(abc.ABC, Generic[A]):
    def __init__(self, expression_type: A):
        self.expression_type: A = expression_type

    @abc.abstractmethod
    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        pass

    def with_type(self, expression_type: "R") -> "BaserowExpression[R]":
        self.expression_type = expression_type
        return self

    def with_valid_type(
        self, expression_type: "type_types.BaserowFormulaValidType"
    ) -> "BaserowExpression[type_types.BaserowFormulaValidType]":
        return self.with_type(expression_type)

    def with_invalid_type(
        self, error: str
    ) -> "BaserowExpression[type_types.BaserowFormulaInvalidType]":
        return self.with_type(type_types.BaserowFormulaInvalidType(error))


class BaserowStringLiteral(BaserowExpression[A]):
    def __init__(self, literal: str, expression_type: A):
        super().__init__(expression_type)

        if not isinstance(literal, str):
            raise InvalidStringLiteralProvided()
        if len(literal) > settings.MAX_FORMULA_STRING_LENGTH:
            raise TooLargeStringLiteralProvided()
        self.literal = literal

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_string_literal(self)

    def __str__(self):
        return self.literal


class BaserowIntegerLiteral(BaserowExpression[A]):
    def __init__(self, literal: int, expression_type: A):
        super().__init__(expression_type)

        if not isinstance(literal, int):
            raise InvalidIntLiteralProvided()
        self.literal = literal

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_int_literal(self)

    def __str__(self):
        return str(self.literal)


class BaserowFieldByIdReference(BaserowExpression[A]):
    def __init__(self, referenced_field_id: int, expression_type: A):
        super().__init__(expression_type)
        self.referenced_field_id = referenced_field_id

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_field_by_id_reference(self)

    def __str__(self):
        return f"field_by_id({self.referenced_field_id})"


class BaserowFieldReference(BaserowExpression[A]):
    def __init__(self, referenced_field_name: str, expression_type: A):
        super().__init__(expression_type)
        self.referenced_field_name = referenced_field_name

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_field_reference(self)

    def __str__(self):
        return f"field({self.referenced_field_name})"


class ArgCountSpecifier(abc.ABC):
    def __init__(self, count):
        self.count = count

    @abc.abstractmethod
    def test(self, num_args: int):
        """
        Should return if the provided num_args matches this ArgCountSpecifier.
        For example if you were extending this class to create a ArgCountSpecifier that
        required the num_args to be less than a fixed number, then here you would check
        return num_args < fixed_number.
        :param num_args: The number of args being provided.
        :return: Whether or not the number of args meets this specification.
        """

        pass

    @abc.abstractmethod
    def __str__(self):
        """
        Should be implemented to explain how to meet this specification in a human
        readable string format.
        """

        pass


class BaserowFunctionCall(BaserowExpression[A]):
    def __init__(
        self,
        function_def: "BaserowFunctionDefinition",
        args: List[BaserowExpression[A]],
        expression_type: A,
    ):
        super().__init__(expression_type)

        self.function_def = function_def
        self.args = args

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_function_call(self)

    def type_function_given_typed_args(
        self,
        args: "List[BaserowExpression[type_types.BaserowFormulaType]]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":
        return self.function_def.type_function_given_typed_args(args, self)

    def type_function_given_valid_args(
        self,
        args: "List[BaserowExpression[type_types.BaserowFormulaValidType]]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":
        return self.function_def.type_function_given_valid_args(args, self)

    def to_django_expression_given_args(
        self,
        args: List[Expression],
    ) -> Expression:
        return self.function_def.to_django_expression_given_args(args)

    def check_arg_type_valid(
        self,
        i: int,
        typed_arg: "BaserowExpression[" "type_types.BaserowFormulaType]",
        all_typed_args: "List[BaserowExpression[type_types.BaserowFormulaType]]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":
        return self.function_def.check_arg_type_valid(i, typed_arg, all_typed_args)

    def with_args(self, new_args) -> "BaserowFunctionCall[A]":
        return BaserowFunctionCall(self.function_def, new_args, self.expression_type)

    def __str__(self):
        optional_type_annotation = (
            f"::{self.expression_type}" if self.expression_type is not None else ""
        )
        args_string = ",".join([str(a) for a in self.args])
        return f"{self.function_def.type}({args_string}){optional_type_annotation}"


class BaserowFunctionDefinition(Instance, abc.ABC):
    """
    A registrable instance which defines a function for use in the Baserow Formula
    language.
    """

    @property
    @abc.abstractmethod
    def type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def num_args(self) -> ArgCountSpecifier:
        pass

    @property
    @abc.abstractmethod
    def arg_types(self) -> "type_types.BaserowArgumentTypeChecker":
        pass

    @abc.abstractmethod
    def type_function_given_valid_args(
        self,
        args: "List[BaserowExpression[type_types.BaserowFormulaValidType]]",
        expression: "BaserowFunctionCall[type_types.UnTyped]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":
        pass

    @abc.abstractmethod
    def to_django_expression_given_args(
        self,
        args: List[Expression],
    ) -> Expression:
        pass

    def type_function_given_typed_args(
        self,
        typed_args: "List[BaserowExpression[type_types.BaserowFormulaType]]",
        expression: "BaserowFunctionCall[type_types.UnTyped]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":
        valid_args: "List[BaserowExpression[type_types.BaserowFormulaValidType]]" = []
        invalid_results: "List[Tuple[int, type_types.BaserowFormulaInvalidType]]" = []
        for i, typed_arg in enumerate(typed_args):
            arg_type = typed_arg.expression_type

            if isinstance(arg_type, type_types.BaserowFormulaInvalidType):
                invalid_results.append((i, arg_type))
            else:
                checked_typed_arg = expression.check_arg_type_valid(
                    i, typed_arg, typed_args
                )
                if isinstance(
                    checked_typed_arg.expression_type,
                    type_types.BaserowFormulaInvalidType,
                ):
                    invalid_results.append((i, checked_typed_arg.expression_type))
                else:
                    valid_args.append(checked_typed_arg)
        if len(invalid_results) > 0:
            message = ", ".join(
                [f"argument {i + 1} {msg.error}" for i, msg in invalid_results]
            )
            return expression.with_invalid_type(
                f"The arguments given to the function call '{self.type}' were invalid "
                f"because: {message}"
            )
        else:
            return self.type_function_given_valid_args(valid_args, expression)

    def call_and_type_with_args(
        self,
        args: "List[BaserowExpression[type_types.BaserowFormulaType]]",
    ) -> "BaserowFunctionCall[type_types.BaserowFormulaType]":
        func_call = BaserowFunctionCall[type_types.UnTyped](self, args, None)
        return func_call.type_function_given_typed_args(args)

    def check_arg_type_valid(
        self,
        i,
        typed_arg: "BaserowExpression[type_types.BaserowFormulaType]",
        all_typed_args: "List[BaserowExpression[type_types.BaserowFormulaType]]",
    ) -> "BaserowExpression[type_types.BaserowFormulaType]":

        if callable(self.arg_types):
            arg_types_for_this_arg = self.arg_types(
                i, [t.expression_type for t in all_typed_args]
            )
        else:
            arg_types_for_this_arg = self.arg_types[i]

        expression_type = typed_arg.expression_type
        for valid_arg_type in arg_types_for_this_arg:
            if isinstance(expression_type, valid_arg_type):
                return typed_arg
        valid_type_names = ",".join(
            [
                formula_type_handler_registry.get_by_model(t).type
                for t in arg_types_for_this_arg
            ]
        )
        expression_type_name = formula_type_handler_registry.get_by_model(
            expression_type
        ).type
        return typed_arg.with_invalid_type(
            f"must be one of the following types '{valid_type_names}' but was "
            f"instead a '{expression_type_name}'"
        )
