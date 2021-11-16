import pytest

from baserow.contrib.database.fields.dependencies.exceptions import (
    CircularFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.handler import FieldDependencyHandler
from baserow.contrib.database.fields.dependencies.models import FieldDependency
from baserow.contrib.database.fields.field_cache import FieldCache


def _unwrap_ids(qs):
    return list(qs.values_list("id", flat=True))


@pytest.mark.django_db
def test_formula_fields_will_be_rebuilt_to_depend_on_each_other(
    api_client, data_fixture, django_assert_num_queries
):
    first_formula_field = data_fixture.create_formula_field(
        name="first", formula_type="text", formula='"a"'
    )
    dependant_formula = data_fixture.create_formula_field(
        name="second",
        table=first_formula_field.table,
        formula_type="text",
        formula="field('first')",
    )

    cache = FieldCache()
    FieldDependencyHandler.rebuild_dependencies(dependant_formula, cache)

    assert _unwrap_ids(dependant_formula.field_dependencies) == [first_formula_field.id]
    assert _unwrap_ids(dependant_formula.dependant_fields) == []

    assert _unwrap_ids(first_formula_field.field_dependencies) == []
    assert _unwrap_ids(first_formula_field.dependant_fields) == [dependant_formula.id]


@pytest.mark.django_db
def test_rebuilding_with_a_circular_ref_will_raise(
    api_client, data_fixture, django_assert_num_queries
):
    first_formula_field = data_fixture.create_formula_field(
        name="first", formula_type="text", formula='field("second")'
    )
    second_formula_field = data_fixture.create_formula_field(
        name="second",
        table=first_formula_field.table,
        formula_type="text",
        formula="field('first')",
    )

    cache = FieldCache()
    FieldDependencyHandler.rebuild_dependencies(first_formula_field, cache)
    with pytest.raises(CircularFieldDependencyError):
        FieldDependencyHandler.rebuild_dependencies(second_formula_field, cache)

    assert _unwrap_ids(second_formula_field.field_dependencies) == []
    assert _unwrap_ids(second_formula_field.dependant_fields) == [
        first_formula_field.id
    ]

    assert _unwrap_ids(first_formula_field.field_dependencies) == [
        second_formula_field.id
    ]
    assert _unwrap_ids(first_formula_field.dependant_fields) == []


@pytest.mark.django_db
def test_rebuilding_a_link_row_field_creates_dependencies_with_vias(
    api_client, data_fixture, django_assert_num_queries
):
    table = data_fixture.create_database_table()
    other_table = data_fixture.create_database_table()
    data_fixture.create_text_field(primary=True, name="primary", table=table)
    other_primary_field = data_fixture.create_text_field(
        primary=True, name="primary", table=other_table
    )
    link_row_field = data_fixture.create_link_row_field(
        name="link", table=table, link_row_table=other_table
    )

    cache = FieldCache()
    FieldDependencyHandler.rebuild_dependencies(link_row_field, cache)

    assert _unwrap_ids(link_row_field.field_dependencies) == [other_primary_field.id]
    assert _unwrap_ids(link_row_field.dependant_fields) == []
    assert link_row_field.vias.count() == 1
    via = link_row_field.vias.get()
    assert via.dependency.id == other_primary_field.id
    assert via.dependant.id == link_row_field.id
    assert via.via.id == link_row_field.id


@pytest.mark.django_db
def test_trashing_a_link_row_field_breaks_vias(
    api_client, data_fixture, django_assert_num_queries
):
    table = data_fixture.create_database_table()
    other_table = data_fixture.create_database_table()
    data_fixture.create_text_field(primary=True, name="primary", table=table)
    field = data_fixture.create_text_field(name="field", table=table)
    other_primary_field = data_fixture.create_text_field(
        primary=True, name="primary", table=other_table
    )
    link_row_field = data_fixture.create_link_row_field(
        name="link", table=table, link_row_table=other_table
    )

    cache = FieldCache()
    FieldDependencyHandler.rebuild_dependencies(link_row_field, cache)

    # Create a fake dependencies until we have lookup fields
    via_dep = FieldDependency.objects.create(
        dependency=other_primary_field, via=link_row_field, dependant=field
    )
    direct_dep = FieldDependency.objects.create(
        dependency=link_row_field, dependant=field
    )

    link_row_field.trashed = True
    link_row_field.save()
    FieldDependencyHandler.rebuild_dependencies(link_row_field, cache)

    # The trashed field is no longer part of the graph
    assert not link_row_field.dependencies.exists()
    assert not link_row_field.vias.exists()
    assert not link_row_field.dependants.exists()

    # The dep that went via the trashed field has been broken
    via_dep.refresh_from_db()
    assert via_dep.dependency is None
    assert via_dep.broken_reference_field_name == "link"
    assert via_dep.via is None

    direct_dep.refresh_from_db()
    assert direct_dep.dependency is None
    assert direct_dep.broken_reference_field_name == "link"
    assert direct_dep.via is None
