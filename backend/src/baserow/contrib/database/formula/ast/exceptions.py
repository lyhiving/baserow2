from django.conf import settings

from baserow.contrib.database.formula.exceptions import BaserowFormulaException


class InvalidStringLiteralProvided(BaserowFormulaException):
    pass


class InvalidIntLiteralProvided(BaserowFormulaException):
    pass


class UnknownFieldReference(BaserowFormulaException):
    def __init__(self, referenced_field):
        super().__init__(f"An unknown field called: {referenced_field} was referenced")


class TooLargeStringLiteralProvided(BaserowFormulaException):
    def __init__(self):
        super().__init__(
            f"an embedded string in the formula over the "
            f"maximum length of {settings.MAX_FORMULA_STRING_LENGTH} "
        )
