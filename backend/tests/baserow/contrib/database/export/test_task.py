from io import BytesIO
from unittest.mock import patch

import pytest

from baserow.contrib.database.export.models import ExportJob
from baserow.contrib.database.export.tasks import export_view, export_view_inner
from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db
@patch("django.core.files.storage.default_storage")
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
        table=table, date_include_time=True, date_format="ISO", name="date_field"
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
            option_field.id: option_b.id,
        },
    )

    stub_file = BytesIO()
    storage_mock.open.return_value = stub_file
    close = stub_file.close
    stub_file.close = lambda: None

    job = ExportJob.objects.create(
        user=user,
        view=grid_view,
        type="csv",
        status="exporting",
    )
    export_view_inner(user.id, grid_view.id, "csv")
    expected = "\ufeffID,text_field,option_field,date_field\r\n'\n '2,atest,2,2020-02-01T01:23:00+00:00\r\n'\n '1,test,2,2020-02-01T01:23:00+00:00\r\n"
    print(expected)
    assert stub_file.getvalue().decode("utf-8") == expected
    close()

    job.refresh_from_db()
    assert job.status == "completed"
    assert job.download_url is not None
