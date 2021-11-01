from typing import List

from django.conf import settings

from baserow.contrib.database.fields.dependencies.exceptions import (
    CircularFieldDependencyError,
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.models import (
    FieldDependencyNode,
    FieldDependencyEdge,
)


def _add_graph_dependency_raising_if_circular(field, referenced_field_name):
    table = field.table
    field_node = field.get_or_create_node()
    referenced_field_dependency_node = _get_or_create_node_from_name(
        referenced_field_name, table
    )
    # Check for no circular references
    if field_node not in referenced_field_dependency_node.self_and_ancestors(
        max_depth=settings.MAX_FIELD_REFERENCE_DEPTH
    ):
        referenced_field_dependency_node.add_child(
            field_node, disable_circular_check=True
        )
    else:
        raise CircularFieldDependencyError()


def _construct_broken_reference_node(referenced_field_name, table):
    node, _ = FieldDependencyNode.objects.get_or_create(
        table=table,
        broken_reference_field_name=referenced_field_name,
    )
    return node


def _get_or_create_node_from_name(referenced_field_name, table):
    from baserow.contrib.database.fields.models import Field

    try:
        referenced_field = table.field_set.get(name=referenced_field_name).specific
        referenced_field_dependency_node = referenced_field.get_or_create_node()
        return referenced_field_dependency_node
    except Field.DoesNotExist:
        return _construct_broken_reference_node(referenced_field_name, table)


def _fix_invalid_refs(field):
    try:
        invalid_node_with_our_name = FieldDependencyNode.objects.get(
            table=field.table,
            field__isnull=True,
            broken_reference_field_name=field.name,
        )
        new_children = FieldDependencyEdge.objects.filter(
            parent=invalid_node_with_our_name
        )
        new_children.update(parent=field.get_or_create_node())
        invalid_node_with_our_name.delete()
        return True
    except FieldDependencyNode.DoesNotExist:
        return False


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
    def update_direct_dependencies_after_field_change(
        cls, field, old_field, rename_only=False
    ):
        _fix_invalid_refs(field)
        updated_fields = []
        node = field.get_or_create_node()
        for other_field_node in node.children.all():
            other_field = other_field_node.field.specific
            other_field_type = field_type_registry.get_by_model(other_field)
            updated_fields += other_field_type.after_direct_field_dependency_changed(
                other_field, field, old_field, rename_only
            )
        return updated_fields

    @classmethod
    def get_direct_same_table_field_dependencies(cls, field):
        node = field.get_or_create_node()
        direct_field_dependencies = []
        for dep in FieldDependencyEdge.objects.filter(child=node).all():
            if dep.via:
                # The dependency points at a field in another table via the dep.via
                # field in this table, so we depend on the via but not the parent
                # field.
                direct_field_dependencies.append(dep.via)
            elif dep.parent.is_reference_to_real_field():
                direct_field_dependencies.append(dep.parent.field)
        return direct_field_dependencies

    @classmethod
    def set_field_dependencies_to(cls, field, dependency_field_names: List[str]):
        field_node = field.get_or_create_node()
        # Delete all existing dependencies this formula_field has as we are about
        # to recreate them
        parent_edges = FieldDependencyEdge.objects.filter(child=field_node)
        # We might have deleted the last edge of an invalid reference. So check
        # and delete it if so.
        for edge in parent_edges.all():
            if edge.parent.is_broken_reference_with_no_dependencies():
                edge.parent.delete()
        parent_edges.delete()

        for new_dependency_field_name in dependency_field_names:
            if field.name == new_dependency_field_name:
                raise SelfReferenceFieldDependencyError()
            _add_graph_dependency_raising_if_circular(field, new_dependency_field_name)
