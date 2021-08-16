from baserow.contrib.database.formula.generated_column_generator.generator import (
    tree_to_generated_column_sql,
)
from baserow.contrib.database.formula.parser.ast_mapper import raw_formula_to_tree


def baserow_formula_to_generated_column_sql(baserow_formula_raw_string: str) -> str:
    """
    Given a raw user input string this function will attempt to parse it as a Baserow
    Formula and then generate a Postgresql generated column SQL expression from it.

    :param baserow_formula_raw_string: A raw user input string which will be checked for
        correctness and converted into generated column sql.
    :return: a SQL expression that can be used in the GENERATED AS {here} part of a
        postgresql generated column definition to calculate the result of the provided
        Baserow Formula.
    :raises GeneratedColumnCompilerException: Is raised when an error occurs when
        generating a generated column from the formula
    :raises BaserowFormulaParserError: Is raised when the provided formula is invalid
        and cannot be parsed.
    """

    return tree_to_generated_column_sql(raw_formula_to_tree(baserow_formula_raw_string))
