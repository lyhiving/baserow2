from baserow.core.registry import Registry


class FormulaFunctionRegistry(Registry):
    name = "formula_function"


formula_function_registry: Registry = FormulaFunctionRegistry()
