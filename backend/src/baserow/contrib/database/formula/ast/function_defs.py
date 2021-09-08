from decimal import Decimal
from typing import Type, List

from django.db.models import (
    Expression,
    Field,
    IntegerField,
    CharField,
    TextField,
    DecimalField,
    FloatField,
    Value,
    Transform,
    Case,
    When,
    BooleanField,
)
from django.db.models.functions import Upper, Lower, Concat

from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
)
from baserow.contrib.database.formula.ast.types import TypeResult


def check_type(
    arg: Field, valid_types: List[Type[Field]], resulting_type: Field
) -> TypeResult:
    for valid_type in valid_types:
        if isinstance(arg, valid_type):
            return TypeResult.valid_type(resulting_type)
    valid_types_str = ",".join([str(t) for t in valid_types])
    return TypeResult.invalid_type(
        f"must be one of {valid_types_str} but was instead {type(arg)}"
    )


def check_types(
    args: List[Field], valid_types: List[Type[Field]], resulting_type: Field
) -> TypeResult:
    invalid_types = []
    for i, arg in enumerate(args):
        arg_type_result = check_type(arg, valid_types, resulting_type)
        if arg_type_result.is_invalid():
            invalid_types.append((i, arg_type_result))
    if len(invalid_types) > 0:
        error = ",".join(
            [f"argument {i} invalid as it {r.error}" for i, r in invalid_types]
        )
        return TypeResult.invalid_type(error)
    else:
        return TypeResult.valid_type(resulting_type)


def register_functions(registry):
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())
    registry.register(BaserowAdd())
    registry.register(BaserowMinus())
    registry.register(BaserowDivide())


class BaserowUpper(BaserowFunctionDefinition):
    type = "upper"

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return Upper(*args)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_type(
            arg=arg_types[0],
            valid_types=[TextField, CharField],
            resulting_type=TextField(),
        )

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowLower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_type(
            arg=arg_types[0],
            valid_types=[TextField, CharField],
            resulting_type=TextField(),
        )

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return Lower(*args)


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_types(
            arg_types,
            [TextField, CharField, IntegerField, DecimalField, FloatField],
            TextField(),
        )

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return Concat(*args, output_field=TextField())


class BaserowAdd(BaserowFunctionDefinition):
    type = "add"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_types_for_decimal(arg_types)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return args[0] + args[1]


def check_types_for_decimal(arg_types, forced_decimal_places=None):
    resulting_type = check_types(arg_types, [DecimalField], DecimalField())
    if resulting_type.is_invalid():
        return resulting_type
    else:
        max_max_digits = 0
        max_decimal_places = 0
        for a in arg_types:
            max_max_digits = max(max_max_digits, a.max_digits)
            max_decimal_places = max(max_decimal_places, a.decimal_places)
        return TypeResult.valid_type(
            DecimalField(
                null=True,
                blank=True,
                max_digits=max_max_digits,
                decimal_places=forced_decimal_places
                if forced_decimal_places is not None
                else max_decimal_places,
            )
        )


class BaserowMinus(BaserowFunctionDefinition):
    type = "minus"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_types_for_decimal(arg_types)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        return args[0] - args[1]


class EqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "="
    arity = 2


class LessThanZeroExpr(Transform):
    template = "%(expressions)s < 0"


class BaserowDivide(BaserowFunctionDefinition):
    type = "divide"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(2)

    def to_django_field_type(self, arg_types: List[Field]) -> TypeResult:
        return check_types_for_decimal(arg_types, forced_decimal_places=5)

    def to_django_expression(self, args: List[Expression]) -> Expression:
        # Prevent divide by zero's by swapping 0 for NaN causing the entire expression
        # to evaluate to NaN.
        return args[0] / Case(
            When(
                condition=(EqualsExpr(args[1], 0, output_field=BooleanField())),
                then=Value(Decimal("NaN")),
            ),
            default=args[1],
        )
