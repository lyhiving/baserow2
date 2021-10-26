import abc

from baserow.contrib.database.fields.registries import field_type_registry


class FieldDependencyHandler:
    @classmethod
    def field_deleted(cls, field, inner_func):
        node = field.get_node()
        if node is not None:
            dependants = [child.field.specific for child in node.children.all()]
            node.field = None
            node.broken_reference_field_name = field.name
            node.save()
        else:
            dependants = []

        inner_func()

        updated_fields = []
        for other_field_node in dependants:
            other_field = other_field_node.field.specific
            other_field_type = field_type_registry.get_by_model(other_field)
            updated_fields += other_field_type.after_direct_field_dependency_changed(
                other_field, None, None
            )
        return updated_fields

    @classmethod
    def update_direct_dependencies_after_field_change(cls, field, rename_only=False):
        updated_fields = []
        node = field.get_or_create_node()
        for other_field_node in node.children.all():
            other_field = other_field_node.field.specific
            other_field_type = field_type_registry.get_by_model(other_field)
            updated_fields += other_field_type.after_direct_field_dependency_changed(
                other_field, field, rename_only
            )
        return updated_fields
