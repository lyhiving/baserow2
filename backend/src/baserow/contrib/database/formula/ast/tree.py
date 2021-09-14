import abc
from typing import List, TypeVar, Generic

from django.conf import settings
from django.db.models import Expression

from baserow.contrib.database.formula.ast import visitors
from baserow.contrib.database.formula.ast.errors import (
    InvalidStringLiteralProvided,
    TooLargeStringLiteralProvided,
    InvalidIntLiteralProvided,
)
from baserow.contrib.database.formula.ast.type_defs import (
    BaserowFormulaInvalidType,
    BaserowFormulaValidType,
    UnTyped,
    BaserowFormulaType,
)
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

    @abc.abstractmethod
    def reduce(self, reduction: R, )
        pass

    # noinspection Mypy
    def with_valid_type(
        self, expression_type: "BaserowFormulaValidType"
    ) -> "BaserowExpression[BaserowFormulaValidType]":
        self.expression_type = expression_type
        return self

    # noinspection Mypy
    def with_invalid_type(
        self, error: str
    ) -> "BaserowExpression[BaserowFormulaInvalidType]":
        self.expression_type = BaserowFormulaInvalidType(error)
        return self


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

    @abc.abstractmethod
    def type_function_given_valid_args(
        self,
        args: "List[BaserowExpression[BaserowFormulaValidType]]",
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> "BaserowExpression[BaserowFormulaType]":
        pass

    @abc.abstractmethod
    def to_django_expression_given_args(
        self,
        args: List[Expression],
    ) -> Expression:
        pass


class BaserowFunctionCall(BaserowExpression[A]):
    def __init__(
        self,
        function_def: BaserowFunctionDefinition,
        args: List[BaserowExpression[A]],
        expression_type: A,
    ):
        super().__init__(expression_type)

        self.function_def = function_def
        self.args = args

    def accept(self, visitor: "visitors.BaserowFormulaASTVisitor[A, T]") -> T:
        return visitor.visit_function_call(self)

    def type_function_given_valid_args(
        self,
        args: "List[BaserowExpression[BaserowFormulaValidType]]",
    ) -> "BaserowExpression[BaserowFormulaType]":
        return self.function_def.type_function_given_valid_args(args, self)

    def to_django_expression_given_args(
        self,
        args: List[Expression],
    ) -> Expression:
        return self.function_def.to_django_expression_given_args(args)

    def __str__(self):
        return f"{self.function_def.type}({','.join([str(a) for a in self.args])})"
