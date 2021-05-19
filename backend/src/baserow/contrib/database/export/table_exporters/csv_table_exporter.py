from typing import List, Dict, BinaryIO, Callable, Any, Iterable, Type

import unicodecsv as csv

from baserow.contrib.database.api.export.serializers import (
    RequestCsvOptionSerializer,
    BaseExporterOptionSerializer,
)
from baserow.contrib.database.export.registries import (
    TableExporter,
    ExporterFunc,
)
from baserow.contrib.database.table.models import FieldObject
from baserow.contrib.database.views.view_types import GridViewType


class CsvTableExporter(TableExporter):
    @property
    def option_serializer_class(self) -> Type[BaseExporterOptionSerializer]:
        return RequestCsvOptionSerializer

    type = "csv"

    @property
    def can_export_table(self) -> bool:
        return True

    @property
    def supported_views(self) -> List[str]:
        return [GridViewType.type]

    @property
    def file_extension(self) -> str:
        return ".csv"

    def make_file_output_generator(
        self,
        ordered_field_objects: Iterable[FieldObject],
        export_options: Dict[any, str],
        export_file: BinaryIO,
    ) -> ExporterFunc:
        ordered_field_database_names = ["id"]
        field_database_name_to_header_value_map = {"id": "ID"}
        ordered_database_field_serializers = [lambda row: ("id", str(row.id))]
        for field_object in ordered_field_objects:
            ordered_database_field_serializers.append(
                _generate_field_serializer(field_object)
            )
            field_database_name = field_object["name"]
            ordered_field_database_names.append(field_database_name)
            field_display_name = field_object["field"].name
            field_database_name_to_header_value_map[
                field_database_name
            ] = field_display_name

        return csv_file_generator(
            ordered_field_database_names,
            field_database_name_to_header_value_map,
            export_file,
            ordered_database_field_serializers,
            **export_options,
        )


def csv_file_generator(
    ordered_field_database_names: List[str],
    field_database_name_to_header_value_map: Dict[str, str],
    file_obj: BinaryIO,
    field_serializers: List[Callable[[Any], Any]],
    csv_charset="utf-8",
    csv_column_separator=",",
    csv_include_header=True,
) -> ExporterFunc:

    # add BOM to support CSVs in MS Excel (for Windows only)
    # TODO is this right??
    if csv_charset == "utf-8":
        file_obj.write(b"\xef\xbb\xbf")

    writer = csv.DictWriter(
        file_obj,
        ordered_field_database_names,
        encoding=csv_charset,
        delimiter=csv_column_separator,
    )

    if csv_include_header:
        writer.writerow(field_database_name_to_header_value_map)

    def write_row(row):
        data = {}
        for f in field_serializers:
            key, value = f(row)
            data[key] = value

        writer.writerow(data)

    return write_row


def _generate_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
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
