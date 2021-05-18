from abc import ABC, abstractmethod
from typing import List, Dict, Any, BinaryIO, Iterable, Tuple, Callable, Type

from django.contrib.auth import get_user_model

from baserow.contrib.database.api.views.grid.grid_view_handler import GridViewHandler
from baserow.contrib.database.table.models import Table, FieldObject
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import GridView, View
from baserow.core.registry import Instance, Registry

User = get_user_model()

ExporterFunc = Callable[[Any], None]
ExportHandlerResult = Tuple[Any, ExporterFunc]


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
    def option_serializer_class(self) -> Type["BaseExporterOptionSerializer"]:
        pass

    def export_view(
        self,
        requesting_user: User,
        view: View,
        export_options: Dict[any, str],
        export_file: BinaryIO,
    ) -> ExportHandlerResult:
        grid_view = ViewHandler().get_view(view.id, GridView)
        # Export to some sort of default queryset function
        rows = GridViewHandler().get_rows(requesting_user, grid_view, search=None)
        ordered_field_objects = []

        model = grid_view.table.get_model()
        for field_id in list(
            grid_view.get_field_options()
            .filter(hidden=False)
            .order_by("field__order")
            .values_list("field__id", flat=True)
        ):
            id_ = model._field_objects[field_id]
            ordered_field_objects.append(id_)

        return rows, self.make_file_output_generator(
            ordered_field_objects,
            export_options,
            export_file,
        )

    def export_table(
        self,
        requesting_user: User,
        table: Table,
        export_options: Dict[str, Any],
        export_file: BinaryIO,
    ) -> ExportHandlerResult:
        table.database.group.has_user(
            requesting_user, raise_error=True, allow_if_template=True
        )
        model = table.get_model()
        queryset = model.objects.all().enhance_by_fields()
        return queryset, self.make_file_output_generator(
            model._field_objects.values(),
            export_options,
            export_file,
        )

    @abstractmethod
    def make_file_output_generator(
        self,
        ordered_field_objects: Iterable[FieldObject],
        export_options: Dict[str, Any],
        export_file: BinaryIO,
    ) -> ExporterFunc:
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
