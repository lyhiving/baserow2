from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
)


def register_functions(registry):
    registry.register(Upper())
    registry.register(Lower())
    registry.register(Concat())


class Upper(BaserowFunctionDefinition):
    type = "upper"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class Lower(BaserowFunctionDefinition):
    type = "lower"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)


class Concat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)
