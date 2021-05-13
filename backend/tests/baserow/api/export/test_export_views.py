from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from freezegun import freeze_time

from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db
def test_field_type_changed(data_fixture, api_client, tmpdir):
    user, token = data_fixture.create_user_and_token()
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
    storage = FileSystemStorage(location=(str(tmpdir)), base_url="http://localhost")

    with patch("baserow.contrib.database.export.handler.default_storage", new=storage):
        with freeze_time("2020-01-02 12:00"):
            response = api_client.post(
                reverse(
                    "api:database:export:export_view", kwargs={"view_id": grid_view.id}
                ),
                data={
                    "exporter_type": "csv",
                    "exporter_options": {
                        "csv_encoding": "utf-8",
                        "csv_include_header": "True",
                        "csv_column_separator": ",",
                    },
                },
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
            job_id = response.json()["id"]
            assert response.json() == {
                "id": job_id,
                "error": None,
                "expires_at": "2020-01-02T13:00:00Z",
                "exported_file_name": None,
                "exporter_type": "csv",
                "progress_percentage": 0.0,
                "status": "pending",
                "table": table.id,
                "view": grid_view.id,
                "url": None,
            }
            response = api_client.get(
                reverse("api:database:export:get", kwargs={"job_id": job_id}),
                format="json",
                HTTP_AUTHORIZATION=f"JWT {token}",
            )
            filename = response.json()["exported_file_name"]
            assert response.json() == {
                "id": job_id,
                "error": None,
                "expires_at": "2020-01-02T13:00:00Z",
                "exported_file_name": filename,
                "exporter_type": "csv",
                "progress_percentage": 1.0,
                "status": "completed",
                "table": table.id,
                "view": grid_view.id,
                "url": f"http://localhost:8000/media/export_files/{filename}",
            }

            file_path = tmpdir.join(settings.EXPORT_FILES_DIRECTORY, filename)
            assert file_path.isfile()
            expected = (
                "\ufeff"
                "ID,text_field,option_field,date_field\n"
                "2,atest,A,02/01/2020 01:23\n"
                "1,test,B,02/01/2020 01:23\n"
            )
            with open(file_path, "r", encoding="utf-8") as written_file:
                assert written_file.read() == expected
