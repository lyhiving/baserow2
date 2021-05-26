from abc import ABC, abstractmethod
from typing import List, Any, Callable, Type

from django.contrib.auth import get_user_model

from baserow.core.registry import Instance, Registry

User = get_user_model()

ExporterFunc = Callable[[Any, bool], None]


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

    @property
    @abstractmethod
    def queryset_serializer_class(self) -> Type["QuerysetSerializer"]:
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
