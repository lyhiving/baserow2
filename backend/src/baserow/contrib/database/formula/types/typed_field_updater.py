from baserow.contrib.database import models


def update_other_fields_referencing_this_fields_name(
    field: "models.Field", new_field_name: str
):
    from baserow.contrib.database.fields.registries import field_type_registry

    old_field_name = field.name
    field_updates = []
    if old_field_name != new_field_name:
        node = field.get_or_create_node()
        for other_field_node in node.children.all():
            other_field = other_field_node.field.specific
            other_field_type = field_type_registry.get_by_model(other_field)
            other_field_type.after_direct_field_dependency_changed(
                other_field, old_field_name, new_field_name
            )
    return field_updates
