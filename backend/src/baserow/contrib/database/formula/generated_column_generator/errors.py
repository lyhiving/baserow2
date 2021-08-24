class GeneratedColumnCompilerException(Exception):
    pass


class UnknownBaserowFunction(GeneratedColumnCompilerException):
    def __init__(self, function_def):
        self.function_def = function_def
        super().__init__(
            f"An unknown function called {function_def.type} was given to the "
            f"generated column compiler."
        )


class UnknownFunctionDefinitionType(GeneratedColumnCompilerException):
    def __init__(self, function_def):
        self.function_def = function_def
        super().__init__(
            f"An unknown function definition of type "
            f"{type(function_def)} was given to the generated column "
            f"compiler."
        )
