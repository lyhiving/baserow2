from typing import Optional, Tuple, List

from django.conf import settings

from baserow.contrib.database.fields.dependencies.exceptions import (
    CircularFieldDependencyError,
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.update_collector import (
    CachingFieldUpdateCollector,
)
from baserow.contrib.database.fields.dependencies.visitors import (
    FieldGraphDependencyVisitor,
)
from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.models import (
    FieldDependencyNode,
    FieldDependencyEdge,
)
from baserow.contrib.database.table import models as table_models


def update_fields_with_broken_references(field: Field):
    """
    Checks to see if any fields

    :param field:
    :type field:
    :return:
    :rtype:
    """

    try:
        broken_node_matching_fields_name = (
            FieldDependencyNode.objects_without_field_join.get(
                table=field.table,
                field__isnull=True,
                broken_reference_field_name=field.name,
            )
        )
        fields_new_children = FieldDependencyEdge.objects.filter(
            parent=broken_node_matching_fields_name
        )
        fields_new_children.update(parent=field.get_or_create_node())
        broken_node_matching_fields_name.delete()
        return True
    except FieldDependencyNode.DoesNotExist:
        return False


class FieldDependencyRebuildingVisitor(FieldGraphDependencyVisitor):
    def __init__(
        self,
        updated_fields_collector: CachingFieldUpdateCollector,
        rebuild_children,
    ):
        super().__init__(updated_fields_collector)
        self.rebuild_children = rebuild_children

    def visit_starting_field(
        self, starting_field: Field, old_starting_field: Optional[Field]
    ):
        _rebuild_field_dependencies(starting_field, self.updated_fields_collector)
        self.updated_fields_collector.add_updated_field(starting_field)

    def visit_field_dependency(
        self,
        child_field: Field,
        parent_field: Field,
        via_field: Optional[Field],
        path_to_starting_field: List[str],
    ):
        if self.rebuild_children:
            _rebuild_field_dependencies(child_field, self.updated_fields_collector)
            self.updated_fields_collector.add_updated_field(child_field)
        return self.rebuild_children


def _add_graph_dependency_raising_if_circular(
    field: Field,
    dependency_field_name: str,
    field_lookup_cache: FieldCache,
    via_field_name: Optional[str] = None,
):
    table = field.table
    field_node = field.get_or_create_node()
    if via_field_name is None:
        dependency_node = _get_or_create_node_from_name(
            table, dependency_field_name, field_lookup_cache
        )
        _add_dep(field_node, dependency_node)
    else:
        _add_dep_with_via(
            field_node, dependency_field_name, table, via_field_name, field_lookup_cache
        )


def _add_dep_with_via(
    field_node: FieldDependencyNode,
    dependency_field_name: str,
    table: "table_models.Table",
    via_field_name: str,
    field_lookup_cache: FieldCache,
):
    via_field = field_lookup_cache.lookup_by_name(table, via_field_name)
    if via_field is None:
        # We are depending on a non existent via field so we have no idea what the
        # target table is. Just create a single broken node for the via field and
        # depend on that.
        broken_node = _construct_broken_reference_node(table, via_field_name)
        _add_dep(field_node, broken_node)
    else:
        from baserow.contrib.database.fields.models import LinkRowField

        if not isinstance(via_field, LinkRowField):
            # We are depending on a via_field which doesn't target another table so
            # we can't actually depend on a target field as we have no idea what the
            # target table is.
            # Instead we depend on the via_field directly so if it's type / name changes
            # we will be updated and possibly fixed.
            _add_dep(field_node, via_field)
        else:
            target_table = via_field.link_row_table
            target_field_node = _get_or_create_node_from_name(
                target_table, dependency_field_name, field_lookup_cache
            )
            _add_dep(field_node, target_field_node, via_field=via_field)


def _add_dep(
    from_node: FieldDependencyNode,
    to_node: FieldDependencyNode,
    via_field: Optional[Field] = None,
):
    # Check for no circular references ourselves rather than using add_child as this
    # way we can set the max_depth of the CTE query.
    if from_node not in to_node.self_and_ancestors(
        max_depth=settings.MAX_FIELD_REFERENCE_DEPTH
    ):
        FieldDependencyEdge.objects.create(
            parent=to_node, child=from_node, via=via_field
        )
    else:
        raise CircularFieldDependencyError()


def _construct_broken_reference_node(
    table: "table_models.Table", broken_reference_field_name: str
):
    node, _ = FieldDependencyNode.objects.get_or_create(
        table=table,
        broken_reference_field_name=broken_reference_field_name,
    )
    return node


def _get_or_create_node_from_name(
    table: "table_models.Table", field_name: str, field_lookup_cache: FieldCache
):
    field = field_lookup_cache.lookup_by_name(table, field_name)
    if field is not None:
        return field.get_or_create_node()
    else:
        return _construct_broken_reference_node(table, field_name)


def _delete_existing_dependencies(field_node):
    parent_edges = FieldDependencyEdge.objects.filter(child=field_node)
    for edge in parent_edges.all():
        # We might have deleted the last edge of an invalid reference. So check
        # and delete it if so.
        if edge.parent.is_broken_reference_with_no_dependencies():
            edge.parent.delete()
    parent_edges.delete()


def _add_dependency(field_instance, dependency, field_lookup_cache):
    if isinstance(dependency, Tuple):
        (
            via_field_name,
            dependency,
        ) = dependency
    else:
        via_field_name = None

    if field_instance.name == dependency:
        raise SelfReferenceFieldDependencyError()
    _add_graph_dependency_raising_if_circular(
        field_instance,
        dependency,
        field_lookup_cache,
        via_field_name=via_field_name,
    )


def _rebuild_field_dependencies(
    field_instance,
    field_lookup_cache: FieldCache,
):
    """
    Deletes all existing dependencies a field has and resets them to the ones
    defined by the field_instances FieldType.get_field_dependencies. Does not
    affect any dependencies from other fields to this field.

    :param field_instance: The field whose dependencies to change.
    :param field_lookup_cache: A cache which will be used to lookup the actual
        fields referenced by any provided field dependencies.
    """

    field_type = field_type_registry.get_by_model(field_instance)
    field_dependencies = field_type.get_field_dependencies(
        field_instance, field_lookup_cache
    )
    if field_dependencies is not None:
        field_node = field_instance.get_or_create_node()
        _delete_existing_dependencies(field_node)
        for dependency in field_dependencies:
            _add_dependency(field_instance, dependency, field_lookup_cache)
