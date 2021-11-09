from copy import deepcopy
from typing import Optional, List

from django.db import connection

from baserow.contrib.database.fields.dependencies.update_collector import (
    CachingFieldUpdateCollector,
)
from baserow.contrib.database.fields.dependencies.visitors import (
    FieldGraphDependencyVisitor,
)
from baserow.contrib.database.formula.types.formula_type import BaserowFormulaType
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_update_django_expression,
)


class BulkMultiTableFormulaFieldRefresher(FieldGraphDependencyVisitor):
    def __init__(
        self,
        updated_fields_collector: CachingFieldUpdateCollector,
        starting_row_id: Optional[int] = None,
        recalculate_field_types: bool = True,
        refresh_field_values: bool = True,
    ):
        super().__init__(updated_fields_collector)
        self.refresh_field_values = refresh_field_values
        self.current_table = None
        self.current_bulk_update_query = {}
        self.model_cache = {}
        self.starting_row_id = starting_row_id
        self.recalculate_field_types = recalculate_field_types
        self.last_path = None

    def only_for_specific_field_types(self) -> Optional[List[str]]:
        from baserow.contrib.database.fields.field_types import FormulaFieldType

        return [FormulaFieldType.type]

    def visit_starting_field(self, starting_field, old_starting_field):
        self._refresh_and_recalculate_field(starting_field, old_starting_field, [])

    def visit_field_dependency(
        self,
        child_field,
        parent_field,
        via_field,
        path_to_starting_field,
    ):
        self._refresh_and_recalculate_field(child_field, None, path_to_starting_field)
        return True

    def _refresh_and_recalculate_field(
        self, field, old_field, path_from_starting_table
    ):
        from baserow.contrib.database.views.handler import ViewHandler

        if old_field is None and self.recalculate_field_types:
            old_field = deepcopy(field)
            field.save(field_lookup_cache=self.updated_fields_collector)
            _recreate_field_if_required(field, old_field)
            ViewHandler().field_type_changed(field)
            self.updated_fields_collector.add_updated_field(field)

        if self.refresh_field_values:
            expression = field.cached_typed_internal_expression
            self._refresh_formula_values_in_bulk(
                field,
                baserow_expression_to_update_django_expression(
                    expression,
                    self._get_model(field),
                ),
                path_from_starting_table,
            )
            self.updated_fields_collector.add_updated_field(field)
            self.last_path = path_from_starting_table

    def after_graph_visit(self):
        if self.last_path is not None and self.refresh_field_values:
            self._execute_current_bulk_update(self.last_path)

    def _refresh_formula_values_in_bulk(
        self, field, update_expression, path_from_starting_table
    ):
        if field.table != self.current_table:
            self._execute_current_bulk_update(path_from_starting_table)
            self.current_table = field.table

        self.current_bulk_update_query[field.db_column] = update_expression

    def _execute_current_bulk_update(self, path_to_start):
        if self.current_table is not None:
            current_model = self.model_cache[self.current_table.id]
            qs = current_model.objects_and_trash
            if self.starting_row_id and len(path_to_start) > 0:
                joined_path_to_id = "__".join(path_to_start) + "__id"
                qs = qs.filter(**{joined_path_to_id: self.starting_row_id})

            qs.update(**self.current_bulk_update_query)
            self.current_bulk_update_query = {}
            self.current_table = None

    def _get_model(self, field):
        table_id = field.table.id
        if table_id not in self.model_cache:
            self.model_cache[table_id] = field.table.get_model()
        return self.model_cache[table_id]


def _check_if_formula_type_change_requires_drop_recreate(
    old_formula_field, new_type: BaserowFormulaType
):
    old_type = old_formula_field.cached_formula_type

    return new_type.should_recreate_when_old_type_was(old_type)


def _recreate_field_if_required(
    field,
    old_field,
):
    if _check_if_formula_type_change_requires_drop_recreate(
        old_field, field.cached_formula_type
    ):
        model = field.table.get_model(fields=[field], add_dependencies=False)
        from baserow.contrib.database.fields.registries import field_converter_registry

        field_converter_registry.get("formula").alter_field(
            old_field,
            field,
            model,
            model,
            model._meta.get_field(old_field.db_column),
            model._meta.get_field(field.db_column),
            None,
            connection,
        )
