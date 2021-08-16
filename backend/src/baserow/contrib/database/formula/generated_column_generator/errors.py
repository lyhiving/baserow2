class GeneratedColumnCompilerException(Exception):
    pass


class UnknownFunctionDefinitionType(GeneratedColumnCompilerException):
    def __init__(self, function_def):
        self.function_def = function_def
        super().__init__(
            f"An unknown function definition of type "
            f"{type(function_def)} was given to the generated column "
            f"compiler."
        )
