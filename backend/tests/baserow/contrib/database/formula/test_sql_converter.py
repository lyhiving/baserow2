import pytest

from baserow.contrib.database.formula.compiler import (
    baserow_formula_to_generated_column_sql,
)
from baserow.contrib.database.formula.parser.errors import BaserowFormulaSyntaxError


def test_convert():
    assert baserow_formula_to_generated_column_sql('upper("test")') == "UPPER('test')"
    assert (
        baserow_formula_to_generated_column_sql('upper("test\\"")') == "UPPER('test\"')"
    )
    assert (
        baserow_formula_to_generated_column_sql("upper('test\\'')")
        == "UPPER('test\\'')"
    )
    assert (
        baserow_formula_to_generated_column_sql(
            """CONCAT(UPPER(LOWER('test')), "test\\"", 'test\\'')"""
        )
        == """UPPER(LOWER('test'))||'test"'||'test\\''"""
    )
    with pytest.raises(BaserowFormulaSyntaxError):
        baserow_formula_to_generated_column_sql("""UPPER('test\\\') || ASCII('b')""")
