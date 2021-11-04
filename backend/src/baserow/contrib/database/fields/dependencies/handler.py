from typing import List, Tuple, Union, Optional

from django.conf import settings
from django.db import transaction

from baserow.contrib.database.fields.dependencies.exceptions import (
    CircularFieldDependencyError,
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.update_collector import (
    FieldUpdateCollector,
    LookupFieldByNameCache,
)
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula import FormulaHandler
from baserow.contrib.database.formula.models import (
    FieldDependencyNode,
    FieldDependencyEdge,
)
from baserow.core.trash.handler import TrashHandler

FieldDependencies = List[Union[str, Tuple[str, str]]]
OptionalFieldDependencies = Optional[FieldDependencies]


def _add_graph_dependency_raising_if_circular(
    field, referenced_field_name, field_lookup_cache, via_field_name=None
):
    table = field.table
    field_node = field.get_or_create_node()
    if via_field_name is None:
        referenced_field_dependency_node = _get_or_create_node_from_name(
            referenced_field_name, table, field_lookup_cache
        )
        _add_dep(field_node, referenced_field_dependency_node)
    else:
        _setup_via_dep(
            field_lookup_cache, field_node, referenced_field_name, table, via_field_name
        )


def _setup_via_dep(
    field_lookup_cache, field_node, referenced_field_name, table, via_field_name
):
    via_field = field_lookup_cache.lookup(table, via_field_name)
    if via_field is None:
        broken_node = _construct_broken_reference_node(via_field_name, table)
        _add_dep(field_node, broken_node)
    else:
        from baserow.contrib.database.fields.models import LinkRowField

        if not isinstance(via_field, LinkRowField):
            # TODO is this right??
            _add_dep(field_node, via_field)
        else:
            target_table = via_field.link_row_table
            looked_up_field_node = _get_or_create_node_from_name(
                referenced_field_name, target_table, field_lookup_cache
            )
            _add_dep(field_node, looked_up_field_node, via_field=via_field)


def _add_dep(from_node, to_node, via_field=None):
    # Check for no circular references
    if from_node not in to_node.self_and_ancestors(
        max_depth=settings.MAX_FIELD_REFERENCE_DEPTH
    ):
        FieldDependencyEdge.objects.create(
            parent=to_node, child=from_node, via=via_field
        )
    else:
        raise CircularFieldDependencyError()


def _construct_broken_reference_node(referenced_field_name, table):
    node, _ = FieldDependencyNode.objects.get_or_create(
        table=table,
        broken_reference_field_name=referenced_field_name,
    )
    return node


def _get_or_create_node_from_name(referenced_field_name, table, field_lookup_cache):
    referenced_field = field_lookup_cache.lookup(table, referenced_field_name)
    if referenced_field is not None:
        referenced_field_dependency_node = referenced_field.get_or_create_node()
        return referenced_field_dependency_node
    else:
        return _construct_broken_reference_node(referenced_field_name, table)


def _update_fields_with_broken_references(field):
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


def _recursively_update_all_descendants(
    edges,
    field_lookup_cache=None,
    changed_parent=None,
    old_changed_parent=None,
    rename_only=False,
    updated_fields=None,
):
    if updated_fields is None:
        updated_fields = FieldUpdateCollector(field_lookup_cache)

    changed_children = []
    for edge in edges:
        child = edge.child
        other_field = child.field.specific
        other_field_type = field_type_registry.get_by_model(other_field)
        (
            optionally_changed_child_field,
            old_child_field,
        ) = other_field_type.after_direct_field_dependency_changed(
            other_field,
            changed_parent,
            old_changed_parent,
            updated_fields,
            edge.via,
            rename_only,
        )
        if optionally_changed_child_field is not None:
            changed_children.append((optionally_changed_child_field, old_child_field))

    # Recursively continue down the field dependency graph now updating all the children
    # of the children which changed this time.
    for optionally_changed_child_field, old_child_field in changed_children:
        FieldDependencyHandler.update_direct_dependencies_after_field_change(
            optionally_changed_child_field,
            old_child_field,
            updated_fields=updated_fields,
        )
    return updated_fields


def _get_direct_descendants_and_break_node(field):
    node = field.get_node_or_none()
    if node is not None:
        edges = [edge for edge in FieldDependencyEdge.objects.filter(parent=node)]
        node.field = None
        node.broken_reference_field_name = field.name
        FieldDependencyEdge.objects.filter(child=node).delete()
        node.save()
    else:
        edges = []
    return edges


def _after_field_dependency_graph_update(updated_fields):
    FormulaHandler.recreate_and_refresh_formula_fields(updated_fields)


def _update_graph_after_delete(edges, field, add_field):
    updated_fields = FieldUpdateCollector()
    if add_field:
        updated_fields.add_field(field, None)
    _recursively_update_all_descendants(edges, updated_fields=updated_fields)
    _after_field_dependency_graph_update(updated_fields)
    return updated_fields


def _recursively_recalculate_fields(
    field_lookup_cache, recalculated_already, specific_field, via_field=None
):
    node = specific_field.get_or_create_node()
    for parent_edge in FieldDependencyEdge.objects.filter(child=node):
        parent_node = parent_edge.parent
        if parent_node.is_reference_to_real_field():
            real_field = field_lookup_cache.lookup(
                parent_node.table, parent_node.field.name
            )
            _recursively_recalculate_fields(
                field_lookup_cache,
                recalculated_already,
                real_field,
                via_field=parent_edge.via,
            )
    if specific_field not in recalculated_already:
        field_type = field_type_registry.get_by_model(specific_field)
        field_type.after_direct_field_dependency_changed(
            specific_field, None, None, field_lookup_cache, via_field
        )
        recalculated_already.add(specific_field)


def _find_connections(starting_table, f, already_checked_nodes):
    if not isinstance(f, FieldDependencyNode):
        node = f.get_node_or_none()
    else:
        node = f
    connections = set()
    if node is not None and node not in already_checked_nodes:
        already_checked_nodes.add(node)
        for edge in FieldDependencyEdge.objects.filter(parent=node):
            child = edge.child
            if child.is_reference_to_real_field():
                if child.table != starting_table and edge.via is not None:
                    connections.add(edge)
                else:
                    connections.update(
                        _find_connections(starting_table, child, already_checked_nodes)
                    )
    return connections


class FieldDependencyHandler:
    @classmethod
    def permanently_delete_and_update_dependencies(cls, field):
        direct_descendants_edges = _get_direct_descendants_and_break_node(field)

        field.delete()

        return _update_graph_after_delete(direct_descendants_edges, field, False)

    @classmethod
    def trash_and_update_dependencies(cls, user, group, field):
        direct_descendants_edges = _get_direct_descendants_and_break_node(field)

        TrashHandler.trash(user, group, field.table.database, field)

        return _update_graph_after_delete(direct_descendants_edges, field, True)

    @classmethod
    def update_field_dependency_graph(
        cls,
        field,
        old_field,
        rename_only=False,
        updated_fields=None,
        field_lookup_cache=None,
    ):
        if updated_fields is None:
            updated_fields = FieldUpdateCollector(field_lookup_cache)

        field_type = field_type_registry.get_by_model(field)
        fixed_some_fields = _update_fields_with_broken_references(field)

        if fixed_some_fields:
            rename_only = False

        dependent_field_names = field_type.get_direct_field_name_dependencies(
            field, updated_fields
        )
        if dependent_field_names is not None:
            cls.reset_field_dependencies_to(
                field, dependent_field_names, updated_fields
            )

        cls.update_direct_dependencies_after_field_change(
            field, old_field, rename_only, updated_fields
        )
        _after_field_dependency_graph_update(updated_fields)
        return updated_fields

    @classmethod
    def update_direct_dependencies_after_field_change(
        cls, field, old_field, rename_only=False, updated_fields=None
    ):
        updated_fields.add_field(field, old_field)
        node = field.get_or_create_node()
        _recursively_update_all_descendants(
            FieldDependencyEdge.objects.filter(parent=node),
            changed_parent=field,
            old_changed_parent=old_field,
            rename_only=rename_only,
            updated_fields=updated_fields,
        )

    @classmethod
    def get_direct_same_table_field_dependencies(cls, field):
        node = field.get_node_or_none()
        if node is None:
            return []
        direct_field_dependencies = []
        for dep in FieldDependencyEdge.objects.filter(child=node).all():
            if dep.via and dep.via != field:
                # The dependency points at a field in another table via the dep.via
                # field in this table, so we depend on the via but not the parent
                # field.
                direct_field_dependencies.append(dep.via)
            elif dep.parent.is_reference_to_real_field():
                direct_field_dependencies.append(dep.parent.field)
        return direct_field_dependencies

    @classmethod
    def reset_field_dependencies_to(
        cls,
        field,
        dependency_field_names: FieldDependencies,
        field_lookup_cache,
        rollback=False,
    ):
        # Ensure that a circular/self reference being thrown resets any changes to the
        # field dependency graph.
        with transaction.atomic():
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
                if isinstance(new_dependency_field_name, Tuple):
                    (
                        via_field_name,
                        new_dependency_field_name,
                    ) = new_dependency_field_name
                    if field.name == new_dependency_field_name:
                        raise SelfReferenceFieldDependencyError()
                    _add_graph_dependency_raising_if_circular(
                        field,
                        new_dependency_field_name,
                        field_lookup_cache,
                        via_field_name=via_field_name,
                    )
                else:
                    if field.name == new_dependency_field_name:
                        raise SelfReferenceFieldDependencyError()
                    _add_graph_dependency_raising_if_circular(
                        field, new_dependency_field_name, field_lookup_cache
                    )
            if rollback:
                transaction.set_rollback(True)

    @classmethod
    def raise_if_any_circular_references(cls, field, field_lookup_cache):
        field_type = field_type_registry.get_by_model(field)
        dependent_field_names = field_type.get_direct_field_name_dependencies(
            field, field_lookup_cache
        )
        if dependent_field_names is not None:
            cls.reset_field_dependencies_to(
                field, dependent_field_names, field_lookup_cache, rollback=True
            )

    @classmethod
    def rebuild_graph(cls, fields):
        field_lookup_cache = LookupFieldByNameCache()
        for specific_field in fields:
            field_type = field_type_registry.get_by_model(specific_field)
            dependency_field_names = field_type.get_direct_field_name_dependencies(
                specific_field, field_lookup_cache
            )
            if dependency_field_names is not None:
                cls.reset_field_dependencies_to(
                    specific_field,
                    dependency_field_names,
                    field_lookup_cache=field_lookup_cache,
                )
            field_lookup_cache.cache_field(specific_field)
        recalculated_already = set()
        for specific_field in fields:
            if specific_field not in recalculated_already:
                _recursively_recalculate_fields(
                    field_lookup_cache, recalculated_already, specific_field
                )

    @classmethod
    def recursively_find_connections_to_other_tables(cls, table, updated_fields):
        already_checked_fields = set()
        connections = set()
        for f in updated_fields:
            connections.update(_find_connections(table, f, already_checked_fields))
        return connections
