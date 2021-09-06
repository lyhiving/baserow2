from typing import List

from django.conf import settings


class BaserowFormulaASTException(Exception):
    pass


class InvalidStringLiteralProvided(BaserowFormulaASTException):
    pass


class InvalidIntLiteralProvided(BaserowFormulaASTException):
    pass


class NoSelfReferencesError(BaserowFormulaASTException):
    def __init__(self):
        super().__init__("a formula field cannot reference itself")


class NoCircularReferencesError(BaserowFormulaASTException):
    def __init__(self, visited_fields: List[str]):
        super().__init__(
            "a formula field cannot result in a circular reference, detected a "
            f"circular reference chain of {'->'.join(visited_fields)}"
        )


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
