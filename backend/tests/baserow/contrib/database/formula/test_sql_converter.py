from baserow.contrib.database.formula.compiler import (
    baserow_formula_to_generated_column_sql,
)


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
