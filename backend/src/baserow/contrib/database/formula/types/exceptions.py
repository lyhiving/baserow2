from typing import List

from baserow.contrib.database.formula.exceptions import BaserowFormulaException


class InvalidFormulaType(BaserowFormulaException):
    pass


class NoCircularReferencesError(BaserowFormulaException):
    def __init__(self, visited_fields: List[str]):
        super().__init__(
            "a formula field cannot result in a circular reference, detected a "
            f"circular reference chain of {'->'.join(visited_fields)}"
        )


class NoSelfReferencesError(BaserowFormulaException):
    def __init__(self):
        super().__init__("a formula field cannot reference itself")


class UnknownFormulaType(BaserowFormulaException):
    pass
