import typing
from collections import OrderedDict
from typing import List, BinaryIO, Callable, Any, Type

import unicodecsv as csv

from baserow.contrib.database.api.export.serializers import (
    CsvExporterOptionsSerializer,
    BaseExporterOptionsSerializer,
)
from baserow.contrib.database.export.file_writer import (
    QuerysetSerializer,
    FileWriter,
)
from baserow.contrib.database.export.registries import (
    TableExporter,
    ExporterFunc,
)
from baserow.contrib.database.table.models import FieldObject
from baserow.contrib.database.views.view_types import GridViewType


class CsvTableExporter(TableExporter):
    @property
    def option_serializer_class(self) -> Type[BaseExporterOptionsSerializer]:
        return CsvExporterOptionsSerializer

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

    @property
    def queryset_serializer_class(self):
        return CsvQuerysetSerializer


class CsvQuerysetSerializer(QuerysetSerializer):
    def __init__(self, queryset, ordered_field_objects):
        super().__init__(queryset, ordered_field_objects)

        self.headers = OrderedDict({"id": "ID"})
        self.ordered_database_field_serializers = [lambda row: ("id", str(row.id))]

        for field_object in self.ordered_field_objects:
            self.ordered_database_field_serializers.append(
                _get_field_serializer(field_object)
            )
            field_database_name = field_object["name"]
            field_display_name = field_object["field"].name
            self.headers[field_database_name] = field_display_name

    def write_to_file(
        self,
        file_writer: FileWriter,
        export_charset="utf-8",
        csv_column_separator=",",
        csv_include_header=True,
    ):
        # add BOM to support utf-8 CSVs in MS Excel (for Windows only)
        if export_charset == "utf-8":
            file_writer.write_bytes(b"\xef\xbb\xbf")

        csv_dict_writer = file_writer.get_csv_dict_writer(
            self.headers.keys(), encoding=export_charset, delimiter=csv_column_separator
        )

        if csv_include_header:
            csv_dict_writer.writerow(self.headers)

        def write_row(row, _):
            data = {}
            for csv_serializer in self.ordered_database_field_serializers:
                field_database_name, field_csv_value = csv_serializer(row)
                data[field_database_name] = field_csv_value

            csv_dict_writer.writerow(data)

        file_writer.write_rows(self.queryset, write_row)


def _get_csv_file_row_export_function(
    headers: typing.OrderedDict[str, str],
    file_obj: BinaryIO,
    csv_field_serializers: List[Callable[[Any], Any]],
    export_charset="utf-8",
    csv_column_separator=",",
    csv_include_header=True,
) -> ExporterFunc:
    """
    Writes out the initial header row if configured to do so and then returns a function
    to write out each actual row in turn.

    :param headers: An ordered dictionary of the database field column name to the
        header that should be written for that column in the csv file.
    :param file_obj: The file to write to.
    :param csv_field_serializers: A list of functions which take the row, serialize one
        of the columns and return the name of the column and its serialized value.
    :param export_charset:
        The charset to write to the csv file with.
    :param csv_column_separator:
        The column separator to generate the csv file with.
    :param csv_include_header:
        True if a header row should be written, False if not.
    :return: A function which when called with a row will write that row as a csv line
        to the file.
    """

    writer = csv.DictWriter(
        file_obj,
        headers.keys(),
        encoding=export_charset,
        delimiter=csv_column_separator,
    )

    if csv_include_header:
        writer.writerow(headers)

    def write_row(row, _):
        data = {}
        for csv_serializer in csv_field_serializers:
            field_database_name, field_csv_value = csv_serializer(row)
            data[field_database_name] = field_csv_value

        writer.writerow(data)

    return write_row


def _get_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
    csv_serializer = field_object["type"].get_csv_serializer_field(
        field_object["field"]
    )

    def csv_serializer_func(row):
        attr = getattr(row, field_object["name"])
        # Because we are using to_representation directly we need to all any querysets
        # ourselves.
        if hasattr(attr, "all"):
            attr = attr.all()

        if attr is None:
            result = ""
        else:
            # We use the to_representation method directly instead of constructing a
            # whole serializer class as this gives us a large (30%+) performance boost
            # compared to generating an entire row serializer and using that on every
            # row.
            result = csv_serializer.to_representation(attr)

        if isinstance(result, list):
            result = ",".join(result)

        return (
            field_object["name"],
            result,
        )

    return csv_serializer_func
