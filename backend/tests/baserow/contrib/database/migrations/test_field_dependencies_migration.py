import pytest
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS

# noinspection PyPep8Naming
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


# noinspection PyPep8Naming
@pytest.mark.django_db
def test_forwards_migration(data_fixture, transactional_db):
    migrate_from = [("database", "0040_formulafield_remove_field_by_id")]
    migrate_to = [("database", "0042_not_null_internal_formula_fields")]

    old_state = migrate(migrate_from)

    # The models used by the data_fixture below are not touched by this migration so
    # it is safe to use the latest version in the test.
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(user=user, table=table, name="text")
    FormulaField = old_state.apps.get_model("database", "FormulaField")
    ContentType = old_state.apps.get_model("contenttypes", "ContentType")
    content_type_id = ContentType.objects.get_for_model(FormulaField).id
    formula_field = FormulaField.objects.create(
        table_id=table.id,
        formula_type="text",
        formula=f"field('{text_field.name}')",
        content_type_id=content_type_id,
        order=0,
        name="a",
    )
    trashed_field = FormulaField.objects.create(
        table_id=table.id,
        formula_type="text",
        formula=f"1",
        content_type_id=content_type_id,
        order=0,
        name="trashed",
        trashed=True,
    )
    FormulaField.objects.create(
        table_id=table.id,
        formula_type="text",
        formula=f"field('{formula_field.name}')",
        content_type_id=content_type_id,
        order=0,
        name="c",
    )
    unknown_field = FormulaField.objects.create(
        table_id=table.id,
        formula_type="invalid",
        formula=f"field('{trashed_field.name}')",
        content_type_id=content_type_id,
        order=0,
        name="b",
    )

    new_state = migrate(migrate_to)
    NewFormulaField = new_state.apps.get_model("database", "FormulaField")

    new_formula_field = NewFormulaField.objects.get(id=formula_field.id)
    assert new_formula_field.formula == formula_field.formula
    assert (
        new_formula_field.internal_formula == f"error_to_null(field('"
        f"{text_field.db_column}'))"
    )
    new_unknown_field = NewFormulaField.objects.get(id=unknown_field.id)
    assert new_unknown_field.formula == unknown_field.formula
    assert new_unknown_field.internal_formula == f"field('trashed')"
    assert new_unknown_field.formula_type == "invalid"

    FieldDependencyNode = new_state.apps.get_model("database", "FieldDependencyNode")
    FieldDependencyEdge = new_state.apps.get_model("database", "FieldDependencyEdge")
    assert FieldDependencyNode.objects.count() == 5
    assert FieldDependencyEdge.objects.count() == 3

    # We need to apply the latest migration otherwise other tests might fail.
    call_command("migrate", verbosity=0, database=DEFAULT_DB_ALIAS)


# noinspection PyPep8Naming
@pytest.mark.django_db
def test_backwards_migration(data_fixture, transactional_db):
    migrate_from = [("database", "0042_not_null_internal_formula_fields")]
    migrate_to = [("database", "0040_formulafield_remove_field_by_id")]

    old_state = migrate(migrate_from)

    # The models used by the data_fixture below are not touched by this migration so
    # it is safe to use the latest version in the test.
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    data_fixture.create_text_field(user=user, table=table, name="text")
    FormulaField = old_state.apps.get_model("database", "FormulaField")
    ContentType = old_state.apps.get_model("contenttypes", "ContentType")
    content_type_id = ContentType.objects.get_for_model(FormulaField).id
    formula_field = FormulaField.objects.create(
        table_id=table.id,
        formula_type="text",
        formula=f"field('text')",
        internal_formula="something",
        requires_refresh_after_insert=False,
        content_type_id=content_type_id,
        order=0,
        name="a",
    )
    unknown_field = FormulaField.objects.create(
        table_id=table.id,
        formula_type="text",
        formula=f"field('unknown')",
        internal_formula="something",
        requires_refresh_after_insert=False,
        content_type_id=content_type_id,
        order=0,
        name="b",
    )

    new_state = migrate(migrate_to)
    NewFormulaField = new_state.apps.get_model("database", "FormulaField")

    new_formula_field = NewFormulaField.objects.get(id=formula_field.id)
    assert new_formula_field.formula == f"field('text')"
    new_unknown_field_by_id = NewFormulaField.objects.get(id=unknown_field.id)
    assert new_unknown_field_by_id.formula == "field('unknown')"

    # We need to apply the latest migration otherwise other tests might fail.
    call_command("migrate", verbosity=0, database=DEFAULT_DB_ALIAS)


def migrate(target):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()  # reload.
    executor.migrate(target)
    new_state = executor.loader.project_state(target)
    return new_state
