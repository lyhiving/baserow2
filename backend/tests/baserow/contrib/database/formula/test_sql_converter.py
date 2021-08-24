import pytest

from baserow.contrib.database.formula.ast.tree import BaserowStringLiteral
from baserow.contrib.database.formula.compiler import (
    baserow_formula_to_generated_column_sql,
)
from baserow.contrib.database.formula.generated_column_generator.generator import (
    tree_to_generated_column_sql,
)
from baserow.contrib.database.formula.parser.ast_mapper import raw_formula_to_tree
from baserow.contrib.database.formula.parser.errors import BaserowFormulaSyntaxError


def test_convert():
    assert baserow_formula_to_generated_column_sql('upper("test")') == "UPPER('test')"
    assert (
        baserow_formula_to_generated_column_sql('upper("test\\"")') == "UPPER('test\"')"
    )
    assert (
        baserow_formula_to_generated_column_sql("upper('test\\'')") == "UPPER('test''')"
    )
    assert (
        baserow_formula_to_generated_column_sql(
            """CONCAT(UPPER(LOWER('test')), "test\\"", 'test\\'')"""
        )
        == """UPPER(LOWER('test'))||'test"'||'test'''"""
    )
    with pytest.raises(BaserowFormulaSyntaxError):
        baserow_formula_to_generated_column_sql("""UPPER('test\\\') || ASCII('b')""")


@pytest.mark.django_db
def test_injection(data_fixture):
    user = data_fixture.create_user()
    table_1 = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table(user=user)

    model = table_2.get_model()
    model.objects.create()
    assert model.objects.count() == 1

    dangerous_formula = (
        f"test') STORED; TRUNCATE TABLE database_table_{table_2.id}; "
        "ALTER TABLE "
        f"database_table_{table_1.id} ADD COLUMN new_test_col text GENERATED ALWAYS "
        "AS ('hah"
    )
    data_fixture.create_formula_field(user=user, formula=f"'{dangerous_formula}'")

    # Assert that the formula above actually does truncate the other table via an
    # injection attack
    assert model.objects.count() == 0

    # Now try again but this time going through a conversion from a Baserow Formula AST
    # to generated column sql. We don't go via the parser as sure, that also adds extra
    # protection, however if in the future other ways of creating the AST are created
    # not via the parser we still want the AST->Generated Column step to be secure.
    model.objects.create()
    assert model.objects.count() == 1

    dangerous_formula2 = (
        f"test\\') STORED; TRUNCATE TABLE database_table_{table_2.id}; "
        "ALTER TABLE "
        f"database_table_{table_1.id} ADD COLUMN new_test_col text GENERATED ALWAYS "
        "AS ('hah"
    )
    dangerous_formula_made_safe = BaserowStringLiteral(dangerous_formula2)
    safe_formula = tree_to_generated_column_sql(dangerous_formula_made_safe)
    assert safe_formula == (
        "'test\\'') STORED; TRUNCATE TABLE database_table_2; ALTER TABLE "
        "database_table_1 ADD COLUMN new_test_col text GENERATED ALWAYS AS (''hah'"
    )
    data_fixture.create_formula_field(user=user, formula=safe_formula)
    assert model.objects.count() == 1
