from typing import Type, List, Union

from django.db.models import (
    Expression,
    Field,
    IntegerField,
    CharField,
    TextField,
    DecimalField,
    FloatField,
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
        return Upper(*args)

    def to_django_field_type(self, arg_types: List[Field]) -> Field:
        check_types(arg_types, [TextField, CharField], "")
        return TextField()

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowLower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def to_django_field_type(self, arg_types: List[Field]) -> Field:
        check_types(arg_types, [TextField, CharField], "")
        return TextField()

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return Lower(*args)


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def to_django_field_type(self, arg_types: List[Field]) -> Field:
        check_types(
            arg_types,
            [TextField, CharField, IntegerField, DecimalField, FloatField],
            "",
        )
        return TextField()

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return Concat(*args, output_field=TextField())


def check_type(arg: Field, field_type: List[Type[Field]], msg=""):
    for t in field_type:
        if isinstance(arg, t):
            return
    raise InvalidTypes(msg + f" but instead was a {arg}")


def check_types(args: List[Field], field_type: List[Type[Field]], msg=""):
    for a in args:
        check_type(a, field_type, msg)


class BaserowAdd(BaserowFunctionDefinition):
    type = "add"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_field_type(self, arg_types: List[Field]) -> Field:
        check_types(arg_types, [IntegerField, DecimalField], "add")
        return IntegerField()

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return args[0] + args[1]


class BaserowMinus(BaserowFunctionDefinition):
    type = "minus"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_field_type(self, arg_types: List[Field]) -> Field:
        check_types(arg_types, [IntegerField, DecimalField], "minus")
        return IntegerField()

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return args[0] - args[1]
