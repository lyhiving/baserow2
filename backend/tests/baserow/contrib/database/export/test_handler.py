from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest

from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db
@patch("baserow.contrib.database.export.handler.default_storage")
def test_can_export_simple_view_to_simple_csv(
    storage_mock, data_fixture, django_assert_num_queries
):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(table=table, name="text_field")
    option_field = data_fixture.create_single_select_field(
        table=table, name="option_field"
    )
    option_a = data_fixture.create_select_option(
        field=option_field, value="A", color="blue"
    )
    option_b = data_fixture.create_select_option(
        field=option_field, value="B", color="red"
    )
    date_field = data_fixture.create_date_field(
        table=table, date_include_time=True, date_format="US", name="date_field"
    )
    price_field = data_fixture.create_number_field(
        table=table,
        name="Price",
        number_type="DECIMAL",
        number_decimal_places=2,
        number_negative=True,
    )
    table_2 = data_fixture.create_database_table(database=table.database)
    other_table_primary_text_field = data_fixture.create_text_field(
        table=table_2, name="text_field", primary=True
    )
    link_field = FieldHandler().create_field(
        user=user,
        table=table,
        type_name="link_row",
        name="Customer",
        link_row_table=table_2,
    )

    grid_view = data_fixture.create_grid_view(table=table)
    data_fixture.create_view_filter(
        view=grid_view, field=text_field, type="contains", value="test"
    )
    data_fixture.create_view_sort(view=grid_view, field=text_field, order="ASC")

    row_handler = RowHandler()
    first_linked_row = row_handler.create_row(
        user=user,
        table=table_2,
        values={
            other_table_primary_text_field.id: "link-test",
        },
    )
    second_linked_row = row_handler.create_row(
        user=user,
        table=table_2,
        values={
            other_table_primary_text_field.id: "link-other-test",
        },
    )
    row_handler.create_row(
        user=user,
        table=table,
        values={
            text_field.id: "test",
            date_field.id: "2020-02-01 01:23",
            option_field.id: option_b.id,
            link_field.id: [first_linked_row.id, second_linked_row.id],
            price_field.id: Decimal(10.2),
        },
    )
    row_handler.create_row(
        user=user,
        table=table,
        values={
            text_field.id: "atest",
            date_field.id: "2020-02-01 01:23",
            option_field.id: option_a.id,
            link_field.id: [second_linked_row.id],
            price_field.id: Decimal(-10.2),
        },
    )

    stub_file = BytesIO()
    storage_mock.open.return_value = stub_file
    close = stub_file.close
    stub_file.close = lambda: None

    handler = ExportHandler()

    job = handler.create_pending_export_job(user, table, grid_view, "csv", {})
    with django_assert_num_queries(44):
        handler.run_export_job(job)
    expected = (
        "\ufeff"
        "ID,text_field,option_field,date_field,Price,Customer\r\n"
        "2,atest,A,02/01/2020 01:23,-10.20,link-other-test\r\n"
        '1,test,B,02/01/2020 01:23,10.20,"link-test,link-other-test"\r\n'
    )
    actual = stub_file.getvalue().decode("utf-8")
    assert actual == expected
    close()

    job.refresh_from_db()
    assert job.status == "completed"

    row_handler.create_row(
        user=user,
        table=table,
        values={
            text_field.id: "atest3",
            date_field.id: "2020-02-01 01:23",
            option_field.id: option_a.id,
            link_field.id: [second_linked_row.id],
            price_field.id: Decimal(-100.2),
        },
    )
    stub_file = BytesIO()
    storage_mock.open.return_value = stub_file
    close = stub_file.close
    stub_file.close = lambda: None

    handler = ExportHandler()

    job = handler.create_pending_export_job(user, table, grid_view, "csv", {})
    with django_assert_num_queries(44):
        handler.run_export_job(job)
    expected = (
        "\ufeff"
        "ID,text_field,option_field,date_field,Price,Customer\r\n"
        "2,atest,A,02/01/2020 01:23,-10.20,link-other-test\r\n"
        "3,atest3,A,02/01/2020 01:23,-100.20,link-other-test\r\n"
        '1,test,B,02/01/2020 01:23,10.20,"link-test,link-other-test"\r\n'
    )
    actual = stub_file.getvalue().decode("utf-8")
    assert actual == expected
    close()

    job.refresh_from_db()
    assert job.status == "completed"


@pytest.mark.django_db
@patch("baserow.contrib.database.export.handler.default_storage")
def test_field_type_changed(storage_mock, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    text_field = data_fixture.create_text_field(table=table, name="text_field")
    option_field = data_fixture.create_single_select_field(
        table=table, name="option_field"
    )
    option_a = data_fixture.create_select_option(
        field=option_field, value="A", color="blue"
    )
    option_b = data_fixture.create_select_option(
        field=option_field, value="B", color="red"
    )
    date_field = data_fixture.create_date_field(
        table=table, date_include_time=True, date_format="US", name="date_field"
    )

    grid_view = data_fixture.create_grid_view(table=table)
    data_fixture.create_view_filter(
        view=grid_view, field=text_field, type="contains", value="test"
    )
    data_fixture.create_view_sort(view=grid_view, field=text_field, order="ASC")

    row_handler = RowHandler()
    row_handler.create_row(
        user=user,
        table=table,
        values={
            text_field.id: "test",
            date_field.id: "2020-02-01 01:23",
            option_field.id: option_b.id,
        },
    )
    row_handler.create_row(
        user=user,
        table=table,
        values={
            text_field.id: "atest",
            date_field.id: "2020-02-01 01:23",
            option_field.id: option_a.id,
        },
    )

    stub_file = BytesIO()
    storage_mock.open.return_value = stub_file
    close = stub_file.close
    stub_file.close = lambda: None

    handler = ExportHandler()
    job = handler.create_pending_export_job(
        user,
        table,
        grid_view,
        "csv",
        {"csv_encoding": "iso-2022-jp", "csv_column_separator": "\t"},
    )
    handler.run_export_job(job)
    expected = (
        "ID\ttext_field\toption_field\tdate_field\r\n"
        "2\tatest\tA\t02/01/2020 01:23\r\n"
        "1\ttest\tB\t02/01/2020 01:23\r\n"
    )
    actual = stub_file.getvalue().decode("iso-2022-jp")
    assert actual == expected
    close()

    job.refresh_from_db()
    assert job.status == "completed"
