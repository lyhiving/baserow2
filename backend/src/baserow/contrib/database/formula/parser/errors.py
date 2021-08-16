class BaserowFormulaParserError(Exception):
    pass


class InvalidNumberOfArguments(Exception):
    def __init__(self, function_def, num_args):
        super().__init__(
            "An invalid number of arguments were provided to the "
            f"function {function_def.type}. It excepts "
            f"{function_def.num_args} but instead {num_args} were given."
        )
