from abc import ABC, abstractmethod
from typing import List

from baserow.core.registry import Instance, Registry


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
    def can_export_table(self) -> bool:
        pass

    @property
    @abstractmethod
    def supported_views(self) -> List[str]:
        pass

    @abstractmethod
    def export_view(self, requesting_user, view, export_options, export_file):
        pass

    @abstractmethod
    def export_table(self, requesting_user, table, export_options, export_file):
        pass


class TableExporterRegistry(Registry):
    """
    The TableExporterRegistry allows you to register new TableExporters which allow the
    user to export tables and/or views of tables.
    """

    name = "table_exporter"


table_exporter_registry = TableExporterRegistry()
