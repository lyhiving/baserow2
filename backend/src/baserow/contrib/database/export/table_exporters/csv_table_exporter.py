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
        # Export to some sort of default queryset function
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
            requesting_user, raise_error=True, allow_if_template=True
        )
        model = table.get_model()
        queryset = model.objects.all().enhance_by_fields()
        ordered_field_names = [
            field_object["name"] for field_object in model._field_objects.values()
        ]
        ordered_field_headers = [
            field_object["field"].name for field_object in model._field_objects.values()
        ]
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
        ordered_field_names.insert(0, "id")
        ordered_field_headers.insert(0, "ID")
        field_serializers = [
            _generate_field_serializer(field_object)
            for field_object in model._field_objects.values()
            if field_object["name"] in ordered_field_names
        ]
        field_serializers.insert(0, lambda i: ("id", str(i.id)))
        return (
            csv_file_generator(
                rows,
                ordered_field_names,
                ordered_field_headers,
                export_file,
                field_serializers,
                **export_options,
            ),
            rows.count(),
        )


def csv_file_generator(
    queryset, field_names, field_headers, file_obj, field_serializers, **kwargs
):
    """
    The main worker function. Writes CSV data to a file object based on the
    contents of the queryset and yields each row.
    """

    csv_kwargs = {"encoding": "utf-8"}

    if "csv_encoding" in kwargs:
        csv_kwargs["encoding"] = kwargs["csv_encoding"]

    if "csv_column_separator" in kwargs:
        csv_kwargs["delimiter"] = kwargs["csv_column_separator"]

    # add BOM to support CSVs in MS Excel (for Windows only)
    # TODO is this right??
    if csv_kwargs["encoding"] == "utf-8":
        yield file_obj.write(b"\xef\xbb\xbf")

    writer = csv.DictWriter(file_obj, field_names, **csv_kwargs)

    name_map = {}
    for i in range(len(field_names)):
        name_map[field_names[i]] = field_headers[i]

    yield writer.writerow(name_map)

    iterator = queryset.all()
    for record in iterator:
        data = {}
        for f in field_serializers:
            key, value = f(record)
            data[key] = value

        yield writer.writerow(data)


def _generate_field_serializer(field_object):
    csv_serializer = field_object["type"].get_csv_serializer_field(
        field_object["field"]
    )

    def csv_serializer_func(row):
        attr = getattr(row, field_object["name"])
        if hasattr(attr, "all"):
            attr = attr.all()

        if attr is None:
            result = ""
        else:
            # We use the to_representation method directly instead of constructing a
            # whole serializer class for performance reasons.
            result = csv_serializer.to_representation(attr)

        if isinstance(result, list):
            result = ",".join(result)
        return (
            field_object["name"],
            result,
        )

    return csv_serializer_func
