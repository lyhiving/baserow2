from baserow.contrib.database.fields.models import FieldNode, FormulaField, Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.ast.tree import BaserowFieldReference


def _lookup_underlying_field_from_reference(
    formula_field_node: FieldNode,
    field_reference: BaserowFieldReference,
    already_typed_fields,
):
    # TODO
    from baserow.contrib.database.formula.types.typer import (
        TypedFieldNode,
    )

    table = formula_field_node.field.table
    try:
        referenced_field = table.field_set.get(
            name=field_reference.referenced_field_name
        ).specific
        field_type = field_type_registry.get_by_model(referenced_field)
        formula_type = field_type.to_baserow_formula_type(referenced_field)
        if isinstance(referenced_field, FormulaField):
            expr = referenced_field.get_typed_expression(already_typed_fields)
        else:
            expr = BaserowFieldReference(referenced_field.db_column, formula_type)
        typed_field_node = TypedFieldNode(
            expr, referenced_field.get_or_create_node(), referenced_field
        )
    except Field.DoesNotExist:
        node, _ = FieldNode.objects.get_or_create(
            table=table, unresolved_field_name=field_reference.referenced_field_name
        )
        typed_field_node = TypedFieldNode(
            field_reference.with_invalid_type(
                f"references the deleted or unknown field "
                f"{field_reference.referenced_field_name}"
            ),
            node,
            None,
        )
    return typed_field_node
