import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaInvalidType,
)
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.views.handler import ViewHandler


@pytest.mark.django_db
def test_creating_a_model_with_formula_field_immediately_populates_it(data_fixture):
    table = data_fixture.create_database_table()
    formula_field = data_fixture.create_formula_field(
        table=table, formula="'test'", formula_type="text"
    )
    formula_field_name = f"field_{formula_field.id}"
    model = table.get_model()
    row = model.objects.create()

    assert getattr(row, formula_field_name) == "test"


@pytest.mark.django_db
def test_adding_a_formula_field_to_an_existing_table_populates_it_for_all_rows(
    data_fixture,
):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    before_model = table.get_model()
    existing_row = before_model.objects.create()
    formula_field = FieldHandler().create_field(
        user, table, "formula", name="formula", formula="'test'"
    )
    formula_field_name = f"field_{formula_field.id}"
    model = table.get_model()
    row = model.objects.create()

    assert getattr(row, formula_field_name) == "test"
    assert getattr(model.objects.get(id=existing_row.id), formula_field_name) == "test"


@pytest.mark.django_db
def test_cant_change_the_value_of_a_formula_field_directly(data_fixture):
    table = data_fixture.create_database_table()
    data_fixture.create_formula_field(
        name="formula", table=table, formula="'test'", formula_type="text"
    )
    data_fixture.create_text_field(name="text", table=table)
    model = table.get_model(attribute_names=True)

    row = model.objects.create(formula="not test")
    assert row.formula == "test"

    row.text = "update other field"
    row.save()

    row.formula = "not test"
    row.save()
    row.refresh_from_db()
    assert row.formula == "test"


@pytest.mark.django_db
def test_get_set_export_serialized_value_formula_field(data_fixture):
    table = data_fixture.create_database_table()
    formula_field = data_fixture.create_formula_field(
        table=table, formula="'test'", formula_type="text"
    )
    formula_field_name = f"field_{formula_field.id}"
    formula_field_type = field_type_registry.get_by_model(formula_field)

    model = table.get_model()
    row_1 = model.objects.create()
    row_2 = model.objects.create()

    old_row_1_value = getattr(row_1, formula_field_name)
    old_row_2_value = getattr(row_2, formula_field_name)

    assert old_row_1_value == "test"
    assert old_row_2_value == "test"

    formula_field_type.set_import_serialized_value(
        row_1,
        formula_field_name,
        formula_field_type.get_export_serialized_value(
            row_1, formula_field_name, {}, None, None
        ),
        {},
        None,
        None,
    )
    formula_field_type.set_import_serialized_value(
        row_2,
        formula_field_name,
        formula_field_type.get_export_serialized_value(
            row_2, formula_field_name, {}, None, None
        ),
        {},
        None,
        None,
    )

    row_1.save()
    row_2.save()

    row_1.refresh_from_db()
    row_2.refresh_from_db()

    assert old_row_1_value == getattr(row_1, formula_field_name)
    assert old_row_2_value == getattr(row_2, formula_field_name)


@pytest.mark.django_db
def test_changing_type_of_other_field_still_results_in_working_filter(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    grid_view = data_fixture.create_grid_view(user, table=table)
    first_formula_field = data_fixture.create_formula_field(
        table=table, formula="'test'", formula_type="text", name="source"
    )
    formula_field_referencing_first_field = data_fixture.create_formula_field(
        table=table, formula="field('source')", formula_type="text"
    )

    data_fixture.create_view_filter(
        user=user,
        view=grid_view,
        field=formula_field_referencing_first_field,
        type="equal",
        value="t",
    )

    # Change the first formula field to be a boolean field, meaning that the view
    # filter on the referencing formula field is now and invalid and should be deleted
    FieldHandler().update_field(user, first_formula_field, formula="1")

    queryset = ViewHandler().get_queryset(grid_view)
    assert not queryset.exists()
    assert queryset.count() == 0


@pytest.mark.django_db
def test_can_use_complex_date_filters_on_formula_field(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    grid_view = data_fixture.create_grid_view(user, table=table)
    data_fixture.create_date_field(user=user, table=table, name="date_field")
    formula_field = data_fixture.create_formula_field(
        table=table, formula="field('date_field')", formula_type="date", name="formula"
    )

    data_fixture.create_view_filter(
        user=user,
        view=grid_view,
        field=formula_field,
        type="date_equals_today",
        value="Europe/London",
    )

    queryset = ViewHandler().get_queryset(grid_view)
    assert not queryset.exists()
    assert queryset.count() == 0


@pytest.mark.django_db
def test_can_use_complex_contains_filters_on_formula_field(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    grid_view = data_fixture.create_grid_view(user, table=table)
    data_fixture.create_date_field(
        user=user, table=table, name="date_field", date_format="US"
    )
    formula_field = data_fixture.create_formula_field(
        table=table,
        formula="field('date_field')",
        formula_type="date",
        name="formula",
        date_format="US",
        date_time_format="24",
    )

    data_fixture.create_view_filter(
        user=user,
        view=grid_view,
        field=formula_field,
        type="contains",
        value="23",
    )

    queryset = ViewHandler().get_queryset(grid_view)
    assert not queryset.exists()
    assert queryset.count() == 0


@pytest.mark.django_db
def test_can_change_formula_type_breaking_other_fields(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    handler = FieldHandler()
    first_formula_field = handler.create_field(
        user=user, table=table, name="1", type_name="formula", formula="1+1"
    )
    second_formula_field = handler.create_field(
        user=user, table=table, type_name="formula", name="2", formula="field('1')+1"
    )
    handler.update_field(
        user=user, field=first_formula_field, new_type_name="formula", formula="'a'"
    )
    second_formula_field.refresh_from_db()
    assert second_formula_field.formula_type == BaserowFormulaInvalidType.type
    assert "argument number 2" in second_formula_field.error


@pytest.mark.django_db
def test_can_still_insert_rows_with_an_invalid_but_previously_date_formula_field(
    data_fixture,
):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    handler = FieldHandler()
    date_field = handler.create_field(
        user=user, table=table, name="1", type_name="date"
    )
    formula_field = handler.create_field(
        user=user, table=table, type_name="formula", name="2", formula="field('1')"
    )
    handler.update_field(user=user, field=date_field, new_type_name="single_select")

    row = RowHandler().create_row(user=user, table=table)
    assert getattr(row, f"field_{formula_field.id}") is None


@pytest.mark.django_db
def test_formula_with_row_id_is_populated_after_creating_row(
    data_fixture,
):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    handler = FieldHandler()
    formula_field = handler.create_field(
        user=user, table=table, type_name="formula", name="2", formula="row_id()"
    )

    row = RowHandler().create_row(user=user, table=table)
    assert getattr(row, f"field_{formula_field.id}") == row.id


@pytest.mark.django_db
def test_can_rename_field_preserving_whitespace(
    data_fixture,
):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    handler = FieldHandler()
    test_field = handler.create_field(
        user=user, table=table, type_name="text", name="a"
    )
    formula_field = handler.create_field(
        user=user, table=table, type_name="formula", name="2", formula=" field('a') \n"
    )

    assert formula_field.formula == f" field('a') \n"

    handler.update_field(user=user, field=test_field, name="b")

    formula_field.refresh_from_db()

    assert formula_field.formula == f" field('b') \n"


@pytest.mark.django_db
def test_can_update_lookup_field_value(
    data_fixture, api_client, django_assert_num_queries
):

    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table2 = data_fixture.create_database_table(user=user, database=table.database)
    table_primary_field = data_fixture.create_text_field(
        name="p", table=table, primary=True
    )
    data_fixture.create_text_field(name="primaryfield", table=table2, primary=True)
    looked_up_field = data_fixture.create_date_field(
        name="lookupfield",
        table=table2,
        date_include_time=False,
        date_format="US",
    )

    linkrowfield = FieldHandler().create_field(
        user,
        table,
        "link_row",
        name="linkrowfield",
        link_row_table=table2,
    )

    table2_model = table2.get_model(attribute_names=True)
    a = table2_model.objects.create(lookupfield=f"2021-02-01", primaryfield="primary a")
    b = table2_model.objects.create(lookupfield=f"2022-02-03", primaryfield="primary b")

    table_model = table.get_model(attribute_names=True)

    table_row = table_model.objects.create()
    table_row.linkrowfield.add(a.id)
    table_row.linkrowfield.add(b.id)
    table_row.save()

    formulafield = FieldHandler().create_field(
        user,
        table,
        "formula",
        name="formulafield",
        formula=f"IF(datetime_format(lookup('{linkrowfield.name}',"
        f"'{looked_up_field.name}'), "
        f"'YYYY')='2021', 'yes', 'no')",
    )
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                f"field_{table_primary_field.id}": None,
                f"field_{linkrowfield.id}": [
                    {"id": a.id, "value": "primary a"},
                    {"id": b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": ["yes", "no"],
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }
    response = api_client.patch(
        reverse(
            "api:database:rows:item",
            kwargs={"table_id": table2.id, "row_id": a.id},
        ),
        {f"field_{looked_up_field.id}": "2000-02-01"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                f"field_{table_primary_field.id}": None,
                f"field_{linkrowfield.id}": [
                    {"id": a.id, "value": "primary a"},
                    {"id": b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": ["no", "no"],
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }


@pytest.mark.django_db
def test_nested_lookup_with_formula(
    data_fixture, api_client, django_assert_num_queries
):
    do_big_test(api_client, data_fixture, django_assert_num_queries)


def do_big_test(api_client, data_fixture, django_assert_num_queries):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table2 = data_fixture.create_database_table(user=user, database=table.database)
    table3 = data_fixture.create_database_table(user=user, database=table.database)
    table_primary_field = data_fixture.create_text_field(
        name="p", table=table, primary=True
    )
    data_fixture.create_text_field(name="p", table=table3, primary=True)
    data_fixture.create_text_field(name="p", table=table2, primary=True)
    data_fixture.create_text_field(name="lookupfield", table=table2)
    linkrowfield = FieldHandler().create_field(
        user,
        table,
        "link_row",
        name="table_linkrowfield",
        link_row_table=table2,
    )
    linkrowfield2 = FieldHandler().create_field(
        user,
        table2,
        "link_row",
        name="table2_linkrowfield",
        link_row_table=table3,
    )
    table3_model = table3.get_model(attribute_names=True)
    table3_a = table3_model.objects.create(p="table3 a")
    table3_model.objects.create(p="table3 b")
    table3_c = table3_model.objects.create(p="table3 c")
    table3_d = table3_model.objects.create(p="table3 d")
    table2_model = table2.get_model(attribute_names=True)
    table2_1 = table2_model.objects.create(lookupfield=f"lookup 1", p=f"primary 1")
    table2_1.table2linkrowfield.add(table3_a.id)
    table2_1.save()
    table2_2 = table2_model.objects.create(lookupfield=f"lookup 2", p=f"primary 2")
    table2_3 = table2_model.objects.create(lookupfield=f"lookup 3", p=f"primary 3")
    table2_3.table2linkrowfield.add(table3_c.id)
    table2_3.table2linkrowfield.add(table3_d.id)
    table2_3.save()
    table_model = table.get_model(attribute_names=True)
    table1_x = table_model.objects.create(p="table1 x")
    table1_x.tablelinkrowfield.add(table2_1.id)
    table1_x.tablelinkrowfield.add(table2_2.id)
    table1_x.save()
    table1_y = table_model.objects.create(p="table1 y")
    table1_y.tablelinkrowfield.add(table2_3.id)
    table1_y.save()
    # with django_assert_num_queries(1):
    lookup_field_prefetch = FieldHandler().create_field(
        user,
        table,
        type_name="formula",
        name="formula",
        formula=f"lookup('{linkrowfield.name}','{linkrowfield2.name}')",
    )
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.json() == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                f"field_{table_primary_field.id}": table1_x.p,
                f"field_{linkrowfield.id}": [
                    {"id": table2_1.id, "value": table2_1.p},
                    {"id": table2_2.id, "value": table2_2.p},
                ],
                f"field_{lookup_field_prefetch.id}": [
                    table3_a.p,
                ],
                "id": table1_x.id,
                "order": "1.00000000000000000000",
            },
            {
                f"field_{table_primary_field.id}": table1_y.p,
                f"field_{linkrowfield.id}": [{"id": table2_3.id, "value": table2_3.p}],
                f"field_{lookup_field_prefetch.id}": [table3_c.p, table3_d.p],
                "id": table1_y.id,
                "order": "1.00000000000000000000",
            },
        ],
    }
