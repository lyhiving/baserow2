from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import utc, make_aware

from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.fields.field_helpers import (
    construct_all_possible_field_kwargs,
)
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.fields.models import SelectOption
from baserow.contrib.database.rows.handler import RowHandler


def _parse_datetime(datetime):
    return make_aware(parse_datetime(datetime), timezone=utc)


def _parse_date(date):
    return parse_date(date)


@pytest.mark.django_db
@patch("baserow.contrib.database.export.handler.default_storage")
def test_can_export_every_interesting_different_field_to_json(
    storage_mock, data_fixture
):
    datetime = _parse_datetime("2020-02-01 01:23")
    date = _parse_date("2020-02-01")
    expected = {
        "text": "text",
        "long_text": "long_text",
        "url": "http://www.google.com",
        "email": "test@example.com",
        "negative_int": -1,
        "positive_int": 1,
        "negative_decimal": Decimal("-1.2"),
        "positive_decimal": Decimal("1.2"),
        "boolean": True,
        "datetime_us": datetime,
        "date_us": date,
        "datetime_eu": datetime,
        "date_eu": date,
        "link_row": None,
        "file": ([{"name": "hashed_name.txt", "visible_name": "a.txt"}],),
        "single_select": lambda: SelectOption.objects.get(value="A"),
        "phone_number": "+4412345678",
    }
    contents = wide_test(
        data_fixture, storage_mock, expected, {"exporter_type": "json"}
    )
    assert (
        contents
        == """[
{
    "id": 1,
    "text": "",
    "long_text": "",
    "url": "",
    "email": "",
    "negative_int": "",
    "positive_int": "",
    "negative_decimal": "",
    "positive_decimal": "",
    "boolean": false,
    "datetime_us": "",
    "date_us": "",
    "datetime_eu": "",
    "date_eu": "",
    "link_row": [],
    "file": [],
    "single_select": "",
    "phone_number": ""
},
{
    "id": 2,
    "text": "text",
    "long_text": "long_text",
    "url": "http://www.google.com",
    "email": "test@example.com",
    "negative_int": -1,
    "positive_int": 1,
    "negative_decimal": "-1.2",
    "positive_decimal": "1.2",
    "boolean": true,
    "datetime_us": "02/01/2020 01:23",
    "date_us": "02/01/2020",
    "datetime_eu": "01/02/2020 01:23",
    "date_eu": "01/02/2020",
    "link_row": [
        "linked_row_1",
        "linked_row_2"
    ],
    "file": [
        {
            "visible_name": "a.txt",
            "url": "http://localhost:8000/media/user_files/hashed_name.txt"
        }
    ],
    "single_select": "A",
    "phone_number": "+4412345678"
}
]
"""
    )


@pytest.mark.django_db
@patch("baserow.contrib.database.export.handler.default_storage")
def test_can_export_every_interesting_different_field_to_xml(
    storage_mock, data_fixture
):
    datetime = _parse_datetime("2020-02-01 01:23")
    date = _parse_date("2020-02-01")
    expected = {
        "text": "text",
        "long_text": "long_text",
        "url": "http://www.google.com",
        "email": "test@example.com",
        "negative_int": -1,
        "positive_int": 1,
        "negative_decimal": Decimal("-1.2"),
        "positive_decimal": Decimal("1.2"),
        "boolean": True,
        "datetime_us": datetime,
        "date_us": date,
        "datetime_eu": datetime,
        "date_eu": date,
        "link_row": None,
        "file": ([{"name": "hashed_name.txt", "visible_name": "a.txt"}],),
        "single_select": lambda: SelectOption.objects.get(value="A"),
        "phone_number": "+4412345678",
    }
    contents = wide_test(data_fixture, storage_mock, expected, {"exporter_type": "xml"})
    expected_url = "http://localhost:8000/media/user_files/hashed_name.txt"
    expected_file_item = (
        f"<item><visible_name>a.txt</visible_name><url>{expected_url}</url></item>"
    )
    assert (
        contents
        == f"""<?xml version="1.0" encoding="utf-8" ?><rows>
    <row>
        <id>1</id>
        <text></text>
        <long_text></long_text>
        <url></url>
        <email></email>
        <negative_int></negative_int>
        <positive_int></positive_int>
        <negative_decimal></negative_decimal>
        <positive_decimal></positive_decimal>
        <boolean>False</boolean>
        <datetime_us></datetime_us>
        <date_us></date_us>
        <datetime_eu></datetime_eu>
        <date_eu></date_eu>
        <link_row></link_row>
        <file></file>
        <single_select></single_select>
        <phone_number></phone_number>
    </row>
    <row>
        <id>2</id>
        <text>text</text>
        <long_text>long_text</long_text>
        <url>http://www.google.com</url>
        <email>test@example.com</email>
        <negative_int>-1</negative_int>
        <positive_int>1</positive_int>
        <negative_decimal>-1.2</negative_decimal>
        <positive_decimal>1.2</positive_decimal>
        <boolean>True</boolean>
        <datetime_us>02/01/2020 01:23</datetime_us>
        <date_us>02/01/2020</date_us>
        <datetime_eu>01/02/2020 01:23</datetime_eu>
        <date_eu>01/02/2020</date_eu>
        <link_row><item>linked_row_1</item><item>linked_row_2</item></link_row>
        <file>{expected_file_item}</file>
        <single_select>A</single_select>
        <phone_number>+4412345678</phone_number>
    </row>
</rows>
"""
    )


def wide_test(data_fixture, storage_mock, expected, options):
    user = data_fixture.create_user()
    database = data_fixture.create_database_application(user=user)
    table = data_fixture.create_database_table(database=database, user=user)
    link_table = data_fixture.create_database_table(database=database, user=user)
    handler = FieldHandler()
    row_handler = RowHandler()
    all_possible_kwargs_per_type = construct_all_possible_field_kwargs(link_table)
    name_to_field_id = {}
    i = 0
    for field_type_name, all_possible_kwargs in all_possible_kwargs_per_type.items():
        for kwargs in all_possible_kwargs:
            field = handler.create_field(
                user=user,
                table=table,
                type_name=field_type_name,
                order=i,
                **kwargs,
            )
            i += 1
            name_to_field_id[kwargs["name"]] = field.id
    grid_view = data_fixture.create_grid_view(table=table)
    row_handler = RowHandler()
    other_table_primary_text_field = data_fixture.create_text_field(
        table=link_table, name="text_field", primary=True
    )

    def add_linked_row(text):
        return row_handler.create_row(
            user=user,
            table=link_table,
            values={
                other_table_primary_text_field.id: text,
            },
        )

    model = table.get_model()

    # A dictionary of field names to a tuple of (value to create the row model with,
    # the expected value of this value after being exported to csv)
    assert expected.keys() == name_to_field_id.keys(), (
        "Please update the dictionary above with what your new field type should look "
        "like when serialized to csv. "
    )
    row_values = {}
    for field_type, val in expected.items():
        if isinstance(val, tuple):
            val = val[0]
        if callable(val):
            val = val()
        if val is not None:
            row_values[f"field_{name_to_field_id[field_type]}"] = val
    # Make a blank row to test empty field conversion also.
    model.objects.create(**{})
    row = model.objects.create(**row_values)
    linked_row_1 = add_linked_row("linked_row_1")
    linked_row_2 = add_linked_row("linked_row_2")
    getattr(row, f"field_{name_to_field_id['link_row']}").add(
        linked_row_1.id, linked_row_2.id
    )
    job, contents = run_export_job_with_mock_storage(
        table, grid_view, storage_mock, user, options
    )
    return contents


def run_export_job_with_mock_storage(
    table, grid_view, storage_mock, user, options=None
):
    if options is None:
        options = {"exporter_type": "csv"}

    if "export_charset" not in options:
        options["export_charset"] = "utf-8"

    stub_file = BytesIO()
    storage_mock.open.return_value = stub_file
    close = stub_file.close
    stub_file.close = lambda: None
    handler = ExportHandler()
    job = handler.create_pending_export_job(user, table, grid_view, options)
    handler.run_export_job(job)
    actual = stub_file.getvalue().decode(options["export_charset"])
    close()
    return job, actual
