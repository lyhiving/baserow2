from copy import deepcopy
from typing import Set

from django.db import connection

from baserow.contrib.database.formula import (
    BaserowFunctionDefinition,
    BaserowFormulaType,
)
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_django_expression,
)
from baserow.contrib.database.formula.types.typer import TypedBaserowFields
from baserow.contrib.database.formula.types.visitors import FunctionsUsedVisitor


def update_formula_field(typed_field):
    formula_field = typed_field.field
    expression = typed_field.typed_expression
    expression_type = expression.expression_type
    expression_type.raise_if_invalid()
    original = deepcopy(formula_field)
    functions_used: Set[BaserowFunctionDefinition] = expression.accept(
        FunctionsUsedVisitor()
    )
    formula_field.requires_refresh_after_insert = any(
        f.requires_refresh_after_insert for f in functions_used
    )
    expression_type.persist_onto_formula_field(formula_field)
    formula_field.internal_formula = str(expression)
    if not original.same_as(formula_field):
        # TODO
        from baserow.contrib.database.views.handler import ViewHandler

        ViewHandler().field_type_changed(formula_field)
        if formula_field.pk:
            _recreate_field_if_required(
                formula_field.table, original, expression_type, formula_field
            )


def update_changed_dependant_fields(fields, starting_field):
    latest_table_query = {}
    current_table = None
    model_cache = {}
    already_typed_fields = TypedBaserowFields()
    for typed_field in fields:
        typed_field.field.save(already_typed_fields=already_typed_fields)

        current_table, latest_table_query = _refresh_field_values(
            current_table, latest_table_query, model_cache, typed_field
        )
    if current_table is not None:
        model_cache[current_table.id].objects_and_trash.update(**latest_table_query)


def _refresh_field_values(current_table, latest_table_query, model_cache, typed_field):
    field = typed_field.field
    if current_table is None:
        current_table = field.table
    # The next field to refresh is not part of the table we've been building up
    # a bulk update statement for. So we evaluate that bulk update and start
    # building up a new update for this new table
    if current_table != field.table:
        model_cache[current_table.id].objects_and_trash.update(**latest_table_query)
        current_table = field.table
        latest_table_query = {}
    if current_table.id not in model_cache:
        model_cache[current_table.id] = current_table.get_model()
    expr = baserow_expression_to_django_expression(
        typed_field.typed_expression, model_cache[current_table.id], None
    )
    if expr is not None and not (field.error or field.trashed):
        latest_table_query[field.db_column] = expr
    return current_table, latest_table_query
