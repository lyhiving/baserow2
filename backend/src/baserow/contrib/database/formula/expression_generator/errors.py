class ExpressionGeneratorException(Exception):
    pass


class UnknownBaserowFunction(ExpressionGeneratorException):
    def __init__(self, function_def):
        self.function_def = function_def
        super().__init__(
            f"An unknown function called {function_def.type} was given to the "
            f"expression generator."
        )


class InvalidTypes(ExpressionGeneratorException):
    pass
