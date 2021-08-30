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

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowLower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)
