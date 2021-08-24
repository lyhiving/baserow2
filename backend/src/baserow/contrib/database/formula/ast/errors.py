from django.conf import settings


class BaserowFormulaASTException(Exception):
    pass


class InvalidStringLiteralProvided(BaserowFormulaASTException):
    pass


class TooLargeStringLiteralProvided(BaserowFormulaASTException):
    def __init__(self):
        super().__init__(
            f"an embedded string in the formula over the "
            f"maximum length of {settings.MAX_FORMULA_STRING_LENGTH} "
        )
