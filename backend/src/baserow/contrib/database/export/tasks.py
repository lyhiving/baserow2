import uuid

from djqscsv import write_csv

from baserow.config.celery import app
from os.path import join


@app.task(bind=True)
def export_view(self, user_id, view_id, export_type):
    export_view_inner(user_id, view_id, export_type)


def make_func(field_serializer):
    return lambda value: field_serializer.to_representation(
        field_serializer.to_internal_value(value)
    )


def export_view_inner(user_id, view_id, export_type):
    from django.conf import settings
    from baserow.contrib.database.export.handler import ExportHandler
    from django.contrib.auth import get_user_model
    from baserow.contrib.database.views.models import GridView
    from baserow.contrib.database.api.views.grid.grid_view_handler import (
        GridViewHandler,
    )
    from baserow.contrib.database.views.handler import ViewHandler
    from django.core.files.storage import default_storage

    User = get_user_model()
    view = ViewHandler().get_view(view_id, GridView)
    user = User.objects.get(id=user_id)
    rows = GridViewHandler().get_rows(user, view, search=None)
    visible_field_db_names_with_order = []
    field_serializer_map = {}
    model = view.table.get_model()
    for field_id in list(
        view.get_field_options()
        .filter(hidden=False)
        .order_by("field__order")
        .values_list("field__id", flat=True)
    ):
        field = f"field_{field_id}"
        visible_field_db_names_with_order.append(field)
        field_object = model._field_objects[field_id]
        serializer_field = field_object["type"].get_csv_serializer_field(
            field_object["field"]
        )
        print(field_object["field"])
        print(serializer_field)
        field_serializer_map[field] = make_func(serializer_field)

    visible_field_db_names_with_order.insert(0, "id")
    rows = rows.values(*visible_field_db_names_with_order)

    assert export_type == "csv"
    filename = str(uuid.uuid4()) + ".csv"
    url = join(settings.EXPORT_FILES_DIRECTORY, filename)
    print("Saving to url")

    with default_storage.open(url, "wb") as csv_file:
        write_csv(rows, csv_file, field_serializer_map=field_serializer_map)
    ExportHandler().finished_export_job(user_id, view_id, export_type, url)
