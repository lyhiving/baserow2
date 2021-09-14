from baserow.contrib.database.formula.ast.errors import UnknownFormulaType
from baserow.core.registry import Registry, ModelRegistryMixin


class BaserowFormulaFunctionRegistry(Registry):
    name = "formula_function"


class BaserowFormulaTypeHandlerRegistry(ModelRegistryMixin, Registry):
    name = "formula_type_handler"
    does_not_exist_exception_class = UnknownFormulaType


formula_function_registry = BaserowFormulaFunctionRegistry()
formula_type_handler_registry = BaserowFormulaTypeHandlerRegistry()
