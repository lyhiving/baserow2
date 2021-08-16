from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
    StandardFunction,
    FunctionTypeSpecifier,
    InlineOperator,
)


def register_functions(registry):
    registry.register(Upper())
    registry.register(Lower())
    registry.register(Concat())


class Upper(BaserowFunctionDefinition):
    @property
    def sql_function(self) -> FunctionTypeSpecifier:
        return StandardFunction("UPPER")

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    @property
    def type(self):
        return "upper"


class Lower(BaserowFunctionDefinition):
    @property
    def sql_function(self) -> FunctionTypeSpecifier:
        return StandardFunction("LOWER")

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(1)

    @property
    def type(self):
        return "lower"


class Concat(BaserowFunctionDefinition):
    @property
    def sql_function(self) -> FunctionTypeSpecifier:
        return InlineOperator("||")

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    @property
    def type(self):
        return "concat"
