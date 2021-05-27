import json
from collections import OrderedDict
from typing import Type, List
from xml.dom.minidom import parseString

import dicttoxml as dicttoxml

from baserow.contrib.database.api.export.serializers import (
    BaseExporterOptionsSerializer,
)
from baserow.contrib.database.export.file_writer import (
    QuerysetSerializer,
    FileWriter,
)
from baserow.contrib.database.export.registries import TableExporter
from baserow.contrib.database.views.view_types import GridViewType


class JSONQuerysetSerializer(QuerysetSerializer):
    def write_to_file(self, file_writer: FileWriter, export_charset="utf-8"):
        file_writer.write("[\n", encoding=export_charset)

        def write_row(row, last_row):
            data = {}
            for field_serializer in self.field_serializers:
                _, field_name, field_csv_value = field_serializer(row)
                data[field_name] = field_csv_value

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
    def write_to_file(self, file_writer: FileWriter, export_charset="utf-8"):
        file_writer.write(
            f'<?xml version="1.0" encoding="{export_charset}" ?>\n<rows>\n',
            encoding=export_charset,
        )

        def write_row(row, _):
            data = OrderedDict()
            for field_serializer in self.field_serializers:
                _, field_name, field_xml_value = field_serializer(row)
                data[field_name] = field_xml_value

            row_xml = dicttoxml.dicttoxml(
                {"row": data},
                root=False,
                attr_type=False,
            )
            # Extract the first node to get rid of the xml declaration at the top
            # as we are creating that ourselves above and don't want a new one per row.
            dom = parseString(row_xml).childNodes[0]
            file_writer.write(
                dom.toprettyxml(indent="    "),
                encoding=export_charset,
            )

        file_writer.write_rows(self.queryset, write_row)
        file_writer.write("</rows>\n", encoding=export_charset)


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
