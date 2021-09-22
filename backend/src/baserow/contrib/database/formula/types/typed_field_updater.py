from typing import Dict, List, Optional

from django.db import connection

from baserow.contrib.database import models
from baserow.contrib.database.fields.field_converters import FormulaFieldConverter
from baserow.contrib.database.fields.models import FormulaField, Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.formula.types.type_handler import (
    BaserowFormulaTypeHandler,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
)
from baserow.contrib.database.formula.types.table_typer import (
    TypedFieldWithReferences,
    TypedBaserowTable,
    type_all_fields_in_table,
)


def _check_if_formula_type_change_requires_drop_recreate(
    old_formula_field: FormulaField, new_type: BaserowFormulaType
):
    old_formula_field_type = old_formula_field.formula_type
    old_handler: BaserowFormulaTypeHandler = formula_type_handler_registry.get(
        old_formula_field_type
    )
    old_type = old_handler.construct_type_from_formula_field(old_formula_field)
    return new_type.should_recreate_when_old_type_was(old_type)


def _recreate_field_if_required(
    table: "models.Table",
    old_field: FormulaField,
    new_type: BaserowFormulaType,
    new_formula_field: FormulaField,
):
    if _check_if_formula_type_change_requires_drop_recreate(old_field, new_type):
        model = table.get_model(fields=[new_formula_field], typed_table=False)
        FormulaFieldConverter().alter_field(
            old_field,
            new_formula_field,
            model,
            model,
            model._meta.get_field(old_field.db_column),
            model._meta.get_field(new_formula_field.db_column),
            None,
            connection,
        )


def _calculate_and_save_updated_fields(
    table: "models.Table",
    field_id_to_typed_field: Dict[int, TypedFieldWithReferences],
    field_which_changed=None,
) -> List[Field]:
    other_changed_fields = {}
    for typed_field in field_id_to_typed_field.values():
        new_field = typed_field.new_field
        if not isinstance(new_field, FormulaField):
            continue

        typed_formula_expression = typed_field.typed_expression
        formula_field_type = typed_formula_expression.expression_type
        # noinspection PyTypeChecker
        original_formula_field: FormulaField = typed_field.original_field

        field_id = original_formula_field.id
        checking_field_which_changed = (
            field_which_changed is not None and field_which_changed.id == field_id
        )
        if checking_field_which_changed:
            formula_field_type.raise_if_invalid()

        if not (new_field.same_as(original_formula_field)):
            new_field.save()
            if not checking_field_which_changed:
                other_changed_fields[new_field.id] = new_field
                _recreate_field_if_required(
                    table, original_formula_field, formula_field_type, new_field
                )

    if field_which_changed is not None:
        # All fields that depend on the field_which_changed need to have their
        # values recalculated as a result, even if their formula or type did not
        # change as a result.
        field_id_to_typed_field[field_which_changed.id].add_all_missing_valid_parents(
            other_changed_fields, field_id_to_typed_field
        )

    return list(other_changed_fields.values())


class TypedBaserowTableWithUpdatedFields(TypedBaserowTable):
    def __init__(
        self,
        typed_fields: Dict[int, TypedFieldWithReferences],
        table: "models.Table",
        initially_updated_field: Optional[Field],
        updated_fields: List[Field],
    ):
        super().__init__(typed_fields)
        self.table = table
        self.initially_updated_field = initially_updated_field
        self.updated_fields = updated_fields
        if self.initially_updated_field is not None:
            self.all_updated_fields = [
                self.initially_updated_field
            ] + self.updated_fields
        else:
            self.all_updated_fields = self.updated_fields
        self.model = self.table.get_model(
            field_ids=[],
            fields=self.all_updated_fields,
            typed_table=self,
        )

    def update_values_for_all_updated_fields(self):
        all_fields_update_dict = {}
        for updated_field in self.all_updated_fields:
            updated_field_type = field_type_registry.get_by_model(updated_field)
            update_dict = updated_field_type.related_field_changed(
                updated_field, self.model
            )
            for key, value in update_dict.items():
                all_fields_update_dict[key] = value
        self.model.objects_and_trash.update(**all_fields_update_dict)


def type_table_and_update_fields_given_changed_field(
    table: "models.Table", changed_field: Field
) -> "TypedBaserowTableWithUpdatedFields":
    typed_fields = type_all_fields_in_table(table)
    updated_fields = _calculate_and_save_updated_fields(
        table, typed_fields, field_which_changed=changed_field
    )
    typed_changed_field = typed_fields[changed_field.id].new_field
    return TypedBaserowTableWithUpdatedFields(
        typed_fields, table, typed_changed_field, updated_fields
    )


def type_table_and_update_fields_given_deleted_field(
    table: "models.Table", deleted_field_id: int, deleted_field_name: str
):
    typed_fields = type_all_fields_in_table(
        table, {deleted_field_id: deleted_field_name}
    )
    updated_fields = _calculate_and_save_updated_fields(table, typed_fields)
    return TypedBaserowTableWithUpdatedFields(typed_fields, table, None, updated_fields)
