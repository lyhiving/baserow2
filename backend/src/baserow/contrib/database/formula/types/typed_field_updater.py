from django.db import connection

from baserow.contrib.database import models
from baserow.contrib.database.fields.models import FormulaField
from baserow.contrib.database.fields.registries import (
    field_converter_registry,
)
from baserow.contrib.database.formula.parser.update_field_names import (
    update_field_names,
)
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaType,
)
from baserow.contrib.database.formula.types.formula_types import (
    construct_type_from_formula_field,
)


def _check_if_formula_type_change_requires_drop_recreate(
    old_formula_field: FormulaField, new_type: BaserowFormulaType
):
    old_type = construct_type_from_formula_field(old_formula_field)
    return new_type.should_recreate_when_old_type_was(old_type)


def _recreate_field_if_required(
    table: "models.Table",
    old_field: FormulaField,
    new_type: BaserowFormulaType,
    new_formula_field: FormulaField,
):
    if _check_if_formula_type_change_requires_drop_recreate(old_field, new_type):
        model = table.get_model(fields=[new_formula_field])
        field_converter_registry.get("formula").alter_field(
            old_field,
            new_formula_field,
            model,
            model,
            model._meta.get_field(old_field.db_column),
            model._meta.get_field(new_formula_field.db_column),
            None,
            connection,
        )


def update_other_fields_referencing_this_fields_name(
    field: "models.Field", new_field_name: str
):
    old_field_name = field.name
    field_updates = []
    if old_field_name != new_field_name:
        node = field.get_or_create_node()
        for other_field_node in node.children.all():
            other_field = other_field_node.field.specific
            if isinstance(other_field, FormulaField):
                old_formula = other_field.formula
                other_field.formula = update_field_names(
                    old_formula, {old_field_name: new_field_name}
                )
                if old_formula != other_field.formula:
                    field_updates.append(other_field)
        FormulaField.objects.bulk_update(field_updates, fields=["formula"])
    return field_updates
