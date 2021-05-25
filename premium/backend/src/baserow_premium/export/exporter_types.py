import json
from typing import Type, List, Iterable, Dict, BinaryIO, Callable, Any

from baserow.contrib.database.api.export.serializers import (
    BaseExporterOptionsSerializer,
)
from baserow.contrib.database.export.registries import TableExporter, ExporterFunc
from baserow.contrib.database.table.models import FieldObject
from baserow.contrib.database.views.view_types import GridViewType


class JSONTableExporter(TableExporter):
    @property
    def option_serializer_class(self) -> Type[BaseExporterOptionsSerializer]:
        return BaseExporterOptionsSerializer

    type = "json"

    @property
    def can_export_table(self) -> bool:
        return True

    @property
    def supported_views(self) -> List[str]:
        return [GridViewType.type]

    @property
    def file_extension(self) -> str:
        return ".json"

    def get_row_export_function(
        self,
        ordered_field_objects: Iterable[FieldObject],
        export_options: Dict[any, str],
        export_file: BinaryIO,
    ) -> ExporterFunc:
        ordered_database_field_serializers = [lambda row: ("id", row.id)]

        for field_object in ordered_field_objects:
            ordered_database_field_serializers.append(
                _get_json_field_serializer(field_object)
            )

        return _get_json_file_row_export_function(
            export_file,
            ordered_database_field_serializers,
            **export_options,
        )


def _get_json_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
    json_serializer = field_object["type"].get_json_serializer_field(
        field_object["field"]
    )

    def json_serializer_func(row):
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
            result = json_serializer.to_representation(attr)

        return (
            field_object["field"].name,
            result,
        )

    return json_serializer_func


def _get_json_file_row_export_function(
    file_obj: BinaryIO,
    json_field_serializers: List[Callable[[Any], Any]],
    export_charset="utf-8",
) -> ExporterFunc:
    """
    Writes out the initial header row if configured to do so and then returns a function
    to write out each actual row in turn.

    :param file_obj: The file to write to.
    :param json_field_serializers: A list of functions which take the row, serialize one
        of the columns and return the name of the column and its serialized value.
    :param export_charset:
        The charset to write to the csv file with.
    :return: A function which when called with a row will write that row as a csv line
        to the file.
    """

    file_obj.write("[\n".encode(export_charset))

    def write_row(row, last_row):
        data = {}
        for json_serializer in json_field_serializers:
            field_database_name, field_csv_value = json_serializer(row)
            data[field_database_name] = field_csv_value

        file_obj.write(json.dumps(data, indent=4).encode(export_charset))
        if not last_row:
            file_obj.write(",\n".encode(export_charset))
        else:
            file_obj.write("\n]\n".encode(export_charset))

    return write_row


class XMLTableExporter(TableExporter):
    @property
    def option_serializer_class(self) -> Type[BaseExporterOptionsSerializer]:
        return BaseExporterOptionsSerializer

    type = "xml"

    @property
    def can_export_table(self) -> bool:
        return True

    @property
    def supported_views(self) -> List[str]:
        return [GridViewType.type]

    @property
    def file_extension(self) -> str:
        return ".xml"

    def get_row_export_function(
        self,
        ordered_field_objects: Iterable[FieldObject],
        export_options: Dict[any, str],
        export_file: BinaryIO,
    ) -> ExporterFunc:
        ordered_database_field_serializers = [lambda row: ("id", row.id)]

        for field_object in ordered_field_objects:
            ordered_database_field_serializers.append(
                _get_xml_field_serializer(field_object)
            )

        return _get_xml_file_row_export_function(
            export_file,
            ordered_database_field_serializers,
            **export_options,
        )


def _get_xml_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
    xml_serializer = field_object["type"].get_xml_serializer_field(
        field_object["field"]
    )

    def json_serializer_func(row):
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
            result = xml_serializer.to_representation(attr)

        return (
            field_object["field"].name,
            result,
        )

    return json_serializer_func


def _get_xml_file_row_export_function(
    file_obj: BinaryIO,
    xml_field_serializers: List[Callable[[Any], Any]],
    export_charset="utf-8",
) -> ExporterFunc:
    """
    Writes out the initial header row if configured to do so and then returns a function
    to write out each actual row in turn.

    :param file_obj: The file to write to.
    :param json_field_serializers: A list of functions which take the row, serialize one
        of the columns and return the name of the column and its serialized value.
    :param export_charset:
        The charset to write to the csv file with.
    :return: A function which when called with a row will write that row as a csv line
        to the file.
    """

    file_obj.write("<rows>\n".encode(export_charset))

    def write_row(row, last_row):
        file_obj.write("    <row>\n".encode(export_charset))
        for xml_serializer in xml_field_serializers:
            field_database_name, field_csv_value = xml_serializer(row)
            field = (
                f"        <{field_database_name}>{field_csv_value}<"
                f"/{field_database_name}>\n"
            )
            file_obj.write(field.encode(export_charset))
        file_obj.write("    </row>\n".encode(export_charset))

        if last_row:
            file_obj.write("</rows>\n".encode(export_charset))

    return write_row
