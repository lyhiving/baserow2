import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaInvalidType,
)
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.views.handler import ViewHandler


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
        "lookup",
        name="formulafield",
        through_field=linkrowfield.id,
        target_field=looked_up_field.id,
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
                f"field_{formulafield.id}": [
                    {"id": a.id, "value": "2021-02-01"},
                    {"id": b.id, "value": "2022-02-03"},
                ],
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
                f"field_{formulafield.id}": [
                    {"id": a.id, "value": "2000-02-01"},
                    {"id": b.id, "value": "2022-02-03"},
                ],
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


@pytest.mark.django_db
def test_can_delete_lookup_field_value(
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

    table_row = table_model.objects.create(p="table row 1")
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
                f"field_{table_primary_field.id}": "table row 1",
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
    response = api_client.delete(
        reverse(
            "api:database:rows:item",
            kwargs={"table_id": table2.id, "row_id": a.id},
        ),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT
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
                f"field_{table_primary_field.id}": "table row 1",
                f"field_{linkrowfield.id}": [
                    {"id": b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": ["no"],
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }


@pytest.mark.django_db
def test_can_delete_double_link_lookup_field_value(
    data_fixture, api_client, django_assert_num_queries
):

    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table2 = data_fixture.create_database_table(user=user, database=table.database)
    table3 = data_fixture.create_database_table(user=user, database=table.database)
    table_primary_field = data_fixture.create_text_field(
        name="p", table=table, primary=True
    )
    data_fixture.create_text_field(name="primaryfield", table=table2, primary=True)
    data_fixture.create_text_field(name="primaryfield", table=table3, primary=True)
    table2_linkrowfield = FieldHandler().create_field(
        user,
        table2,
        "link_row",
        name="linkrowfield",
        link_row_table=table3,
    )
    table3_model = table3.get_model(attribute_names=True)
    table3_1 = table3_model.objects.create(primaryfield="table 3 row 1")
    table3_2 = table3_model.objects.create(primaryfield="table 3 row 2")

    linkrowfield = FieldHandler().create_field(
        user,
        table,
        "link_row",
        name="linkrowfield",
        link_row_table=table2,
    )

    table2_model = table2.get_model(attribute_names=True)
    table2_a = table2_model.objects.create(primaryfield="primary a")
    table2_a.linkrowfield.add(table3_1.id)
    table2_a.save()
    table2_b = table2_model.objects.create(primaryfield="primary b")
    table2_b.linkrowfield.add(table3_2.id)
    table2_b.save()

    table_model = table.get_model(attribute_names=True)

    table_row = table_model.objects.create(p="table row 1")
    table_row.linkrowfield.add(table2_a.id)
    table_row.linkrowfield.add(table2_b.id)
    table_row.save()

    formulafield = FieldHandler().create_field(
        user,
        table,
        "formula",
        name="formulafield",
        formula=f"lookup('{linkrowfield.name}','{table2_linkrowfield.name}')",
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
                f"field_{table_primary_field.id}": "table row 1",
                f"field_{linkrowfield.id}": [
                    {"id": table2_a.id, "value": "primary a"},
                    {"id": table2_b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": ["table 3 row 1", "table 3 row 2"],
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }
    response = api_client.delete(
        reverse(
            "api:database:rows:item",
            kwargs={"table_id": table2.id, "row_id": table2_a.id},
        ),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT
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
                f"field_{table_primary_field.id}": "table row 1",
                f"field_{linkrowfield.id}": [
                    {"id": table2_b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": ["table 3 row 2"],
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }

    with django_assert_num_queries(1):
        response = api_client.delete(
            reverse(
                "api:database:rows:item",
                kwargs={"table_id": table3.id, "row_id": table3_2.id},
            ),
            format="json",
            HTTP_AUTHORIZATION=f"JWT {token}",
        )
    assert response.status_code == HTTP_204_NO_CONTENT
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
                f"field_{table_primary_field.id}": "table row 1",
                f"field_{linkrowfield.id}": [
                    {"id": table2_b.id, "value": "primary b"},
                ],
                f"field_{formulafield.id}": None,
                "id": table_row.id,
                "order": "1.00000000000000000000",
            }
        ],
    }
