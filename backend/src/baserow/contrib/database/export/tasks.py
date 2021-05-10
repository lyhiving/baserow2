import unicodecsv as csv
import uuid
from rest_framework import serializers

from baserow.config.celery import app
from os.path import join

from baserow.contrib.database.api.rows.serializers import (
    get_row_serializer_class,
)


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

    model = view.table.get_model()
    for field_id in list(
        view.get_field_options()
        .filter(hidden=False)
        .order_by("field__order")
        .values_list("field__id", flat=True)
    ):
        field = f"field_{field_id}"
        visible_field_db_names_with_order.append(field)

    visible_field_db_names_with_order.insert(0, "id")

    row_serializer = get_row_serializer_class(
        model,
        serializers.ModelSerializer,
        field_names=visible_field_db_names_with_order,
        serializer_type="csv",
    )

    assert export_type == "csv"
    filename = str(uuid.uuid4()) + ".csv"
    url = join(settings.EXPORT_FILES_DIRECTORY, filename)
    with default_storage.open(url, "wb") as csv_file:
        write_csv(
            rows,
            visible_field_db_names_with_order,
            csv_file,
            row_serializer=row_serializer,
        )
    ExportHandler().finished_export_job(user_id, view_id, export_type, url)


def write_csv(queryset, field_names, file_obj, **kwargs):
    """
    Writes CSV data to a file object based on the contents of the queryset.
    """
    # Force iteration over all rows so they all get written to the file
    for _ in _iter_csv(queryset, field_names, file_obj, **kwargs):
        pass


def _iter_csv(queryset, field_names, file_obj, **kwargs):
    """
    The main worker function. Writes CSV data to a file object based on the
    contents of the queryset and yields each row.
    """

    # process keyword arguments to pull out the ones used by this function
    row_serializer = kwargs.get("row_serializer", {})

    csv_kwargs = {"encoding": "utf-8"}

    if "encoding" in kwargs:
        csv_kwargs["encoding"] = kwargs["encoding"]

    # add BOM to support CSVs in MS Excel (for Windows only)
    yield file_obj.write(b"\xef\xbb\xbf")

    values_qs = queryset

    writer = csv.DictWriter(file_obj, field_names, **csv_kwargs)

    name_map = dict((field, field) for field in field_names)
    name_map.update(
        dict(
            (field.name, field.verbose_name)
            for field in queryset.model._meta.fields
            if field.name in field_names
        )
    )

    yield writer.writerow(name_map)

    for record in values_qs.all().iterator(chunk_size=2000):
        record = row_serializer(record).data
        yield writer.writerow(record)
