from django.conf import settings


class BaserowFormulaASTException(Exception):
    pass


class InvalidStringLiteralProvided(BaserowFormulaASTException):
    pass


class InvalidIntLiteralProvided(BaserowFormulaASTException):
    pass


class NoSelfReferencesError(BaserowFormulaASTException):
    pass


class NoCircularReferencesError(BaserowFormulaASTException):
    pass


class InvalidFieldType(BaserowFormulaASTException):
    pass


class UnknownFieldReference(BaserowFormulaASTException):
    def __init__(self, referenced_field):
        super().__init__(f"An unknown field called: {referenced_field} was referenced")


class TooLargeStringLiteralProvided(BaserowFormulaASTException):
    def __init__(self):
        super().__init__(
            f"an embedded string in the formula over the "
            f"maximum length of {settings.MAX_FORMULA_STRING_LENGTH} "
        )
