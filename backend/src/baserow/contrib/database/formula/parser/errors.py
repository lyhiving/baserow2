class BaserowFormulaParserError(Exception):
    pass


class InvalidNumberOfArguments(BaserowFormulaParserError):
    def __init__(self, function_def, num_args):
        super().__init__(
            "An invalid number of arguments were provided to the "
            f"function {function_def.type}. It excepts "
            f"{function_def.num_args} but instead {num_args} were given"
        )


class MaximumFormulaDepthError(BaserowFormulaParserError):
    def __init__(self):
        super().__init__("it exceeded the maximum formula size")


class BaserowFormulaSyntaxError(BaserowFormulaParserError):
    pass
