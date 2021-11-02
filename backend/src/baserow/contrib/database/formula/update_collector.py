from django.db import connection

from baserow.contrib.database.formula import FormulaHandler, BaserowFormulaType


class BulkMultiTableFormulaFieldUpdater:
    def __init__(self):
        self.current_table = None
        self.current_bulk_update_query = {}
        self.model_cache = {}

    def run_updates(self, updated_fields):
        for field, old_field in updated_fields.fields:
            if not field.same_as(old_field):
                _recreate_field_if_required(field, old_field)
                self.add_update_for(
                    field,
                    FormulaHandler.baserow_expression_to_django_expression(
                        field.typed_expression, self._get_model(field), None
                    ),
                )
        self.execute_current_bulk_update()

    def add_update_for(self, field, update_expression):
        if field.table != self.current_table:
            self.execute_current_bulk_update()
            self.current_table = field.table

        self.current_bulk_update_query[field.db_column] = update_expression

    def execute_current_bulk_update(self):
        if self.current_table is not None:
            self.current_table.get_model().objects_and_trash.update(
                **self.current_bulk_update_query
            )
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
    old_type = old_formula_field.calculated_expression_type
    return new_type.should_recreate_when_old_type_was(old_type)


def _recreate_field_if_required(
    field,
    old_field,
):
    if _check_if_formula_type_change_requires_drop_recreate(
        old_field, field.calculated_expression_type
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
