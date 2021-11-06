from django.db import connection

from baserow.contrib.database.formula.types.formula_type import BaserowFormulaType
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_update_django_expression,
)


class BulkMultiTableFormulaFieldRefresher:
    def __init__(self):
        self.current_table = None
        self.current_bulk_update_query = {}
        self.model_cache = {}

    def recreate_and_refresh_updated_fields(self, updated_fields):
        from baserow.contrib.database.views.handler import ViewHandler
        from baserow.contrib.database.fields.models import FormulaField

        for (
            updated_field,
            old_field,
        ) in updated_fields.ordered_updated_and_old_fields.values():
            if isinstance(updated_field, FormulaField):
                print(f"refreshing {updated_field}")
                if old_field is not None:
                    _recreate_field_if_required(updated_field, old_field)
                    ViewHandler().field_type_changed(updated_field)
                expression = updated_field.cached_typed_internal_expression
                self._refresh_formula_values_in_bulk(
                    updated_field,
                    baserow_expression_to_update_django_expression(
                        expression,
                        self._get_model(updated_field),
                    ),
                )
            else:
                print("is not formula not refreshing")
                print(updated_field)
        # Ensure we execute any final pending update statements
        self._execute_current_bulk_update()

    def _refresh_formula_values_in_bulk(self, field, update_expression):
        if field.table != self.current_table:
            self._execute_current_bulk_update()
            self.current_table = field.table

        self.current_bulk_update_query[field.db_column] = update_expression

    def _execute_current_bulk_update(self):
        if self.current_table is not None:
            current_model = self.model_cache[self.current_table.id]
            current_model.objects_and_trash.update(**self.current_bulk_update_query)
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
