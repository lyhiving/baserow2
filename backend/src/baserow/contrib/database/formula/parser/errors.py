from baserow.contrib.database.formula.errors import BaserowFormulaException


class InvalidNumberOfArguments(BaserowFormulaException):
    def __init__(self, function_def, num_args):
        super().__init__(
            "An invalid number of arguments were provided to the "
            f"function {function_def.type}. It excepts "
            f"{function_def.num_args} but instead {num_args} were given"
        )


class MaximumFormulaSizeError(BaserowFormulaException):
    def __init__(self):
        super().__init__("it exceeded the maximum formula size")


class UnexpectedFieldReference(BaserowFormulaException):
    pass


class UnknownFieldReference(BaserowFormulaException):
    pass


class UnknownUnaryOperator(BaserowFormulaException):
    def __init__(self, operatorText):
        super().__init__(f"unknown binary operator {operatorText}")


class UnknownBinaryOperator(BaserowFormulaException):
    def __init__(self, operatorText):
        super().__init__(f"unknown binary operator {operatorText}")


class BaserowFormulaSyntaxError(BaserowFormulaException):
    pass
