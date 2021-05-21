from abc import ABC, abstractmethod
from typing import List, Dict, Any, BinaryIO, Iterable, Callable, Type

from django.contrib.auth import get_user_model

from baserow.contrib.database.table.models import FieldObject
from baserow.core.registry import Instance, Registry

User = get_user_model()

ExporterFunc = Callable[[Any], None]


class TableExporter(Instance, ABC):
    """
    This abstract class is the base for a particular way of exporting a table and views
    of a table. A TableExporter defines which views it supports and then the user
    will be able to use the exporter to export views of those types. Additionally if
    can_export_table returns True a the user will also be allowed export a table
    without specifying a particular view.
    """

    @property
    @abstractmethod
    def file_extension(self) -> str:
        pass

    @property
    @abstractmethod
    def can_export_table(self) -> bool:
        pass

    @property
    @abstractmethod
    def supported_views(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def option_serializer_class(self) -> Type["BaseExporterOptionsSerializer"]:
        pass

    @abstractmethod
    def get_row_export_function(
        self,
        ordered_field_objects: Iterable[FieldObject],
        export_options: Dict[str, Any],
        export_file: BinaryIO,
    ) -> ExporterFunc:
        """
        Implement this function in your exporter to control how exactly the export_file
        is generated. It should return a function which when called with a row to export
        writes the row in the correct format to the provided export_file.
        :param ordered_field_objects: An ordered list of fields to export.
        :param export_options: The validated export options returned from
            the option_serializer_class property above.
        :param export_file: A file object to write each row to.
        :return: A function taking one argument, a row to export to the file. Each call
            of the function should output the provided row to the file.
        """
        pass


class TableExporterRegistry(Registry):
    """
    The TableExporterRegistry allows you to register new TableExporters which allow the
    user to export tables and/or views of tables.
    """

    name = "table_exporter"

    def get_option_serializer_map(self):
        return {
            table_exporter_type.type: table_exporter_type.option_serializer_class
            for table_exporter_type in self.registry.values()
        }


table_exporter_registry = TableExporterRegistry()
