from django.db.models import Expression

from baserow.contrib.database.formula.expression_generator.generator import (
    tree_to_django_expression,
)
from baserow.contrib.database.formula.parser.ast_mapper import raw_formula_to_tree
from baserow.contrib.database.formula.parser.errors import MaximumFormulaDepthError


def baserow_formula_to_django_expression(baserow_formula_raw_string: str) -> Expression:
    """
    Given a raw user input string this function will attempt to parse it as a Baserow
    Formula and then generate a django expression which calculates its value.

    :param baserow_formula_raw_string: A raw user input string which will be checked for
        correctness and converted into generated column sql.
    :return: a SQL expression that can be used in the GENERATED AS {here} part of a
        postgresql generated column definition to calculate the result of the provided
        Baserow Formula.
    :raises ExpressionGeneratorException: Is raised when an error occurs when
        generating a Django expression from the formula.
    :raises BaserowFormulaParserError: Is raised when the provided formula is invalid
        and cannot be parsed.
    """

    try:
        return tree_to_django_expression(
            raw_formula_to_tree(baserow_formula_raw_string)
        )
    except RecursionError:
        raise MaximumFormulaDepthError()
