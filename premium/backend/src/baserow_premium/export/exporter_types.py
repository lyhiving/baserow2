import json
from typing import Type, List, Callable, Any

from baserow.contrib.database.api.export.serializers import (
    BaseExporterOptionsSerializer,
)
from baserow.contrib.database.export.file_writer import (
    QuerysetSerializer,
    FileWriter,
)
from baserow.contrib.database.export.registries import TableExporter
from baserow.contrib.database.table.models import FieldObject
from baserow.contrib.database.views.view_types import GridViewType


class JSONQuerysetSerializer(QuerysetSerializer):
    def __init__(self, queryset, ordered_field_objects):
        super().__init__(queryset, ordered_field_objects)
        self.ordered_database_field_serializers = [lambda row: ("id", row.id)]

        for field_object in self.ordered_field_objects:
            self.ordered_database_field_serializers.append(
                self._get_json_field_serializer(field_object)
            )

    @staticmethod
    def _get_json_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
        json_serializer = field_object["type"].get_json_serializer_field(
            field_object["field"]
        )

        def json_serializer_func(row):
            attr = getattr(row, field_object["name"])
            # Because we are using to_representation directly we need to all any
            # querysets ourselves.
            if hasattr(attr, "all"):
                attr = attr.all()

            if attr is None:
                result = ""
            else:
                # We use the to_representation method directly instead of
                # constructing a whole serializer class as this gives us a large (
                # 30%+) performance boost compared to generating an entire row
                # serializer and using that on every row.
                result = json_serializer.to_representation(attr)

            return (
                field_object["field"].name,
                result,
            )

        return json_serializer_func

    def write_to_file(self, file_writer: FileWriter, export_charset="utf-8"):
        file_writer.write("[\n", encoding=export_charset)

        def write_row(row, last_row):
            data = {}
            for json_serializer in self.ordered_database_field_serializers:
                field_database_name, field_csv_value = json_serializer(row)
                data[field_database_name] = field_csv_value

            file_writer.write(json.dumps(data, indent=4), encoding=export_charset)
            if not last_row:
                file_writer.write(",\n", encoding=export_charset)

        file_writer.write_rows(self.queryset, write_row)
        file_writer.write("\n]\n", encoding=export_charset)


class JSONTableExporter(TableExporter):
    @property
    def queryset_serializer_class(self) -> Type["QuerysetSerializer"]:
        return JSONQuerysetSerializer

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


class XMLQuerysetSerializer(QuerysetSerializer):
    def __init__(self, queryset, ordered_field_objects):
        super().__init__(queryset, ordered_field_objects)
        self.ordered_database_field_serializers = [lambda row: ("id", row.id)]

        for field_object in self.ordered_field_objects:
            self.ordered_database_field_serializers.append(
                self._get_xml_field_serializer(field_object)
            )

    def write_to_file(self, file_writer: FileWriter, export_charset="utf-8"):
        file_writer.write(
            f'<?xml version="1.0" encoding="{export_charset}" ?><rows>\n',
            encoding=export_charset,
        )

        def write_row(row, _):
            file_writer.write("    <row>\n", encoding=export_charset)
            for xml_serializer in self.ordered_database_field_serializers:
                field_database_name, field_xml_value = xml_serializer(row)
                field_xml_value = to_xml(field_xml_value)
                field = (
                    f"        <{field_database_name}>{field_xml_value}<"
                    f"/{field_database_name}>\n"
                )
                file_writer.write(field, encoding=export_charset)
            file_writer.write("    </row>\n", encoding=export_charset)

        def to_xml(field_xml_value):
            if isinstance(field_xml_value, list):
                field_xml_value = "".join(
                    [f"<item>{to_xml(v)}</item>" for v in field_xml_value]
                )
            if isinstance(field_xml_value, dict):
                field_xml_value = "".join(
                    [
                        f"<{key}>{to_xml(val)}</{key}>"
                        for key, val in field_xml_value.items()
                    ]
                )
            return field_xml_value

        file_writer.write_rows(self.queryset, write_row)
        file_writer.write("</rows>\n", encoding=export_charset)

    @staticmethod
    def _get_xml_field_serializer(field_object: FieldObject) -> Callable[[Any], Any]:
        xml_serializer = field_object["type"].get_xml_serializer_field(
            field_object["field"]
        )

        def xml_serializer_func(row):
            attr = getattr(row, field_object["name"])
            # Because we are using to_representation directly we need to all any
            # querysets ourselves.
            if hasattr(attr, "all"):
                attr = attr.all()

            if attr is None:
                result = ""
            else:
                # We use the to_representation method directly instead of
                # constructing a whole serializer class as this gives us a large (
                # 30%+) performance boost compared to generating an entire row
                # serializer and using that on every row.
                result = xml_serializer.to_representation(attr)

            return (
                field_object["field"].name,
                result,
            )

        return xml_serializer_func


class XMLTableExporter(TableExporter):
    @property
    def queryset_serializer_class(self) -> Type["QuerysetSerializer"]:
        return XMLQuerysetSerializer

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
