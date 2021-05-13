import unicodecsv as csv
from typing import List

from rest_framework import serializers


from baserow.contrib.database.api.rows.serializers import (
    get_row_serializer_class,
)
from baserow.contrib.database.api.views.grid.grid_view_handler import GridViewHandler
from baserow.contrib.database.export.registries import TableExporter
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import GridView
from baserow.contrib.database.views.view_types import GridViewType


class CsvTableExporter(TableExporter):
    type = "csv"

    def can_export_table(self) -> bool:
        return True

    def supported_views(self) -> List[str]:
        return [GridViewType.type]

    def export_view(self, requesting_user, view, export_options, export_file):
        grid_view = ViewHandler().get_view(view.id, GridView)
        rows = GridViewHandler().get_rows(requesting_user, grid_view, search=None)
        ordered_field_names = []
        ordered_field_headers = []

        model = grid_view.table.get_model()
        for field_id in list(
            grid_view.get_field_options()
            .filter(hidden=False)
            .order_by("field__order")
            .values_list("field__id", flat=True)
        ):
            field = f"field_{field_id}"
            ordered_field_names.append(field)
            ordered_field_headers.append(model._field_objects[field_id]["field"].name)

        ordered_field_names.insert(0, "id")
        ordered_field_headers.insert(0, "ID")

        return self._construct_csv_file_generator(
            model,
            ordered_field_names,
            ordered_field_headers,
            rows,
            export_options,
            export_file,
        )

    def export_table(self, requesting_user, table, export_options, export_file):
        table.database.group.has_user(
            requesting_user.user, raise_error=True, allow_if_template=True
        )
        model = table.get_model()
        queryset = model.objects.all().enhance_by_fields()
        ordered_field_names = [
            field_object["name"] for field_object in model._field_objects.values()
        ]
        ordered_field_headers = [
            field_object["field"].name for field_object in model._field_objects.values()
        ]
        ordered_field_names.insert(0, "id")
        ordered_field_headers.insert(0, "ID")
        return self._construct_csv_file_generator(
            model,
            ordered_field_names,
            ordered_field_headers,
            queryset,
            export_options,
            export_file,
        )

    @staticmethod
    def _construct_csv_file_generator(
        model,
        ordered_field_names,
        ordered_field_headers,
        rows,
        export_options,
        export_file,
    ):
        row_serializer = get_row_serializer_class(
            model,
            serializers.ModelSerializer,
            field_names=ordered_field_names,
            serializer_type="csv",
        )
        return (
            csv_file_generator(
                rows,
                ordered_field_names,
                ordered_field_headers,
                export_file,
                row_serializer=row_serializer,
                **export_options,
            ),
            rows.count(),
        )


def csv_file_generator(queryset, field_names, field_headers, file_obj, **kwargs):
    """
    The main worker function. Writes CSV data to a file object based on the
    contents of the queryset and yields each row.
    """

    # process keyword arguments to pull out the ones used by this function
    row_serializer = kwargs.get("row_serializer", {})

    csv_kwargs = {"encoding": "utf-8"}

    if "csv_encoding" in kwargs:
        csv_kwargs["encoding"] = kwargs["csv_encoding"]

    if "csv_column_separator" in kwargs:
        csv_kwargs["delimiter"] = kwargs["csv_column_separator"]

    # add BOM to support CSVs in MS Excel (for Windows only)
    # TODO is this right??
    if csv_kwargs["encoding"] == "utf-8":
        yield file_obj.write(b"\xef\xbb\xbf")

    values_qs = queryset

    writer = csv.DictWriter(file_obj, field_names, **csv_kwargs)

    name_map = {}
    for i in range(len(field_names)):
        name_map[field_names[i]] = field_headers[i]

    yield writer.writerow(name_map)

    for record in values_qs.all().iterator(chunk_size=2000):
        serialized = row_serializer(record)
        yield writer.writerow(serialized.data)
