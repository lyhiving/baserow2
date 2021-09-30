from baserow.contrib.database.formula.types.exceptions import UnknownFormulaType
from baserow.core.registry import Registry, ClsRegistryMixin


class BaserowFormulaFunctionRegistry(Registry):
    name = "formula_function"


class BaserowFormulaTypeTypeRegistry(ClsRegistryMixin, Registry):
    name = "formula_type_handler"
    does_not_exist_exception_class = UnknownFormulaType


formula_function_registry = BaserowFormulaFunctionRegistry()
formula_type_handler_registry = BaserowFormulaTypeTypeRegistry()
