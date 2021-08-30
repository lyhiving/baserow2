from typing import Type

from django.db.models import Func
from django.db.models.functions import Upper, Lower, Concat

from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
)


def register_functions(registry):
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())


class BaserowUpper(BaserowFunctionDefinition):
    type = "upper"

    def to_django_function(self) -> Type[Func]:
        return Upper

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowLower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    def to_django_function(self) -> Type[Func]:
        return Lower


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def to_django_function(self) -> Type[Func]:
        return Concat
