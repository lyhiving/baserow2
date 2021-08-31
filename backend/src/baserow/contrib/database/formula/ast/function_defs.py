from typing import Type, List, Union

from django.db.models import (
    Expression,
    Field,
    FloatField,
    IntegerField,
    CharField,
    TextField,
)
from django.db.models.functions import Upper, Lower, Concat

from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
)
from baserow.contrib.database.formula.expression_generator.errors import InvalidTypes


def register_functions(registry):
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())
    registry.register(BaserowAdd())
    registry.register(BaserowMinus())


class BaserowUpper(BaserowFunctionDefinition):
    type = "upper"

    def to_django_expression(self, args: List[Expression]) -> Expression:
        check_types(args, [TextField, CharField], "")
        return Upper(*args)

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowLower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        check_types(args, [TextField, CharField], "")
        return Lower(*args)


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        check_types(args, [TextField, CharField], "")
        return Concat(*args)


def check_type(expression: Expression, field_type: List[Type[Field]], msg):
    expression_output_field = expression.output_field
    for t in field_type:
        if isinstance(expression_output_field, t):
            return
    raise InvalidTypes(
        msg + f" but instead was a " f"{expression_output_field.__class__.__name__}"
    )


def check_types(expressions: List[Expression], field_type: List[Type[Field]], msg):
    for e in expressions:
        check_type(e, field_type, msg)


class BaserowAdd(BaserowFunctionDefinition):
    type = "add"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        check_type(args[0], [IntegerField, FloatField], "Arg 1 to + must be a number")
        check_type(args[1], [IntegerField, FloatField], "Arg 2 to + must be a number")
        return args[0] + args[1]


class BaserowMinus(BaserowFunctionDefinition):
    type = "minus"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        check_type(args[0], [IntegerField, FloatField], "Arg 1 to + must be a number")
        check_type(args[1], [IntegerField, FloatField], "Arg 2 to + must be a number")
        return args[0] - args[1]
