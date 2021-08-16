import abc

from baserow.core.registry import Instance


class ArgCountSpecifier(abc.ABC):
    def __init__(self, count):
        self.count = count

    @abc.abstractmethod
    def test(self, num_args):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass


class FixedNumOfArgs(ArgCountSpecifier):
    def __str__(self):
        return f"exactly {self.count} arguments"

    def test(self, num_args):
        return self.count == num_args


class NumOfArgsGreaterThan(ArgCountSpecifier):
    def __str__(self):
        return f"more than {self.count} arguments"

    def test(self, num_args):
        return self.count <= num_args


class FunctionTypeSpecifier(abc.ABC):
    def __init__(self, name):
        self.name = name


class StandardFunction(FunctionTypeSpecifier):
    pass


class InlineOperator(FunctionTypeSpecifier):
    pass


class BaserowFunctionDefinition(Instance, abc.ABC):
    @property
    @abc.abstractmethod
    def type(self):
        pass

    @property
    @abc.abstractmethod
    def num_args(self) -> ArgCountSpecifier:
        pass

    @property
    @abc.abstractmethod
    def sql_function(self) -> FunctionTypeSpecifier:
        pass
