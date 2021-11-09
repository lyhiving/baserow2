from typing import Optional, List, Iterable

from django.db import transaction

from baserow.contrib.database.fields.dependencies.depedency_rebuilder import (
    FieldDependencyRebuildingVisitor,
    _rebuild_field_dependencies,
    update_fields_with_broken_references,
)
from baserow.contrib.database.fields.dependencies.update_collector import (
    CachingFieldUpdateCollector,
)
from baserow.contrib.database.fields.dependencies.visitors import (
    FieldGraphDependencyVisitor,
    FieldGraphRenamingVisitor,
)
from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.field_updater import (
    BulkMultiTableFormulaFieldRefresher,
)
from baserow.contrib.database.formula.models import (
    FieldDependencyEdge,
)
from baserow.core.trash.handler import TrashHandler


def _visit_all_dependencies_breadth_first(
    starting_path: List[str],
    starting_edges: Iterable[FieldDependencyEdge],
    visitors: List[FieldGraphDependencyVisitor],
    field_lookup_cache: FieldCache,
):
    """
    Given some starting dependencies in the field graph this runs the visitors over each
    dependency.
    Each visitor can choose to continue visiting down the graph to the next of
    set dependencies or not.

    Dependencies will be visited breadth first. This means given a field graph that
    looks like:

    X
    │ <- Starting Dependency (X<-A, meaning field A depends on field X)
    A (1)
    ├─ B (2)
    │  ├─ D (4)
    │  ├─ E (5)
    │
    ├─ C (3)
    │  ├─ F (6)
    │  ├─ G (7)

    Starting with the starting dependency of X<-A this function will visit the
    dependencies in the following order: X<-A, A<-B, A<-C, B<-D, B<-E, C<-F, C<-G.

    This is done because imagine we have a field dependency graph that looks like a
    diamond:
    X
    │ <- Starting dependency (X<-A, meaning field A depends on field X)
    A (1)
    ├─ B (2)
    │  ├─ D (4)
    │  │
    ├─ C (3)

    This means field D depends on field B and C, and both B and C depend on A.
    If we did instead a depth first traversal we would calculate in this order:
    X<-A, A<-B, B<-D, A<-C which would result in D have incorrect values as it depends
    on C but C had not yet been visited when D was visited.

    :param starting_edges: The dependenies to start traversing the field graph.
    :param visitors: The starting visitors which will visit the starting_edges and
        then depending on each visitor will continue or not visiting further edges.
    :param field_lookup_cache: A cache used to lookup fields from the database.
    """

    deps_with_visitors = [(e, visitors, starting_path) for e in starting_edges]
    while len(deps_with_visitors) > 0:
        dependency, visitors, path = deps_with_visitors.pop(0)
        child_field = field_lookup_cache.lookup_specific(dependency.child.field)
        if dependency.parent.field is not None:
            parent_field = field_lookup_cache.lookup_specific(dependency.parent.field)
        else:
            parent_field = None

        if dependency.via:
            path = [dependency.via.db_column] + path

        # Call the visitors who wanted to visit this dependency
        remaining_visitors = []
        field_type = field_type_registry.get_by_model(child_field)
        for v in visitors:
            if v.accepts(field_type):
                visit_child = v.visit_field_dependency(
                    child_field, parent_field, dependency.via, path
                )
                if visit_child:
                    remaining_visitors.append(v)
        # Only continue visiting edges of this child_field if there is a visitor who
        # wants to continue for this particular dependencies child.
        if remaining_visitors:
            deps_with_visitors += [
                (e, remaining_visitors, path)
                for e in _direct_non_broken_dependency_edges(child_field)
            ]


def _direct_non_broken_dependency_edges(field):
    node = field.get_node_or_none()
    if node is None:
        return []
    else:
        return (
            FieldDependencyEdge.objects.filter(parent=node)
            .filter(child__field__isnull=False)
            .select_related("child__field")
        )


def _get_direct_descendants_and_break_node(field):
    node = field.get_node_or_none()
    if node is not None:
        edges = [edge for edge in _direct_non_broken_dependency_edges(field)]
        node.field = None
        node.broken_reference_field_name = field.name
        # Delete any dependencies this node might have had.
        FieldDependencyEdge.objects.filter(child=node).delete()
        node.save()
    else:
        edges = []
    return edges


def _visit_all_dependencies(
    visitors: List[FieldGraphDependencyVisitor],
    field: Optional[Field] = None,
    old_field: Optional[Field] = None,
    starting_edges: Optional[List[FieldDependencyEdge]] = None,
    field_lookup_cache=None,
):
    if field_lookup_cache is None:
        field_lookup_cache = FieldCache()

    if field is not None:
        field_lookup_cache.cache_field(field)
        field_type = field_type_registry.get_by_model(field)
        for v in visitors:
            if v.accepts(field_type):
                v.visit_starting_field(field, old_field)

    if starting_edges is None:
        starting_edges = _direct_non_broken_dependency_edges(field)

    _visit_all_dependencies_breadth_first(
        [],
        starting_edges,
        visitors,
        field_lookup_cache,
    )

    for v in visitors:
        v.after_graph_visit()


def _field_deleted_visitors(updated_fields: CachingFieldUpdateCollector):
    return [
        FieldDependencyRebuildingVisitor(updated_fields, rebuild_first_children=True),
        BulkMultiTableFormulaFieldRefresher(
            updated_fields,
            recalculate_internal_formulas=True,
            refresh_row_values=True,
        ),
    ]


def _field_changed_visitors(
    changed_field: Optional[Field],
    old_changed_field: Optional[Field],
    rename_only: bool,
    updated_fields: CachingFieldUpdateCollector,
):
    visitors = []
    if changed_field is not None and old_changed_field is not None:
        old_name = old_changed_field.name
        new_name = changed_field.name
        if old_name != new_name:
            visitors.append(
                FieldGraphRenamingVisitor(updated_fields, old_name, new_name)
            )
    if not rename_only:
        visitors += [
            FieldDependencyRebuildingVisitor(updated_fields),
            BulkMultiTableFormulaFieldRefresher(
                updated_fields,
                recalculate_internal_formulas=True,
                refresh_row_values=True,
            ),
        ]
    return visitors


class FieldDependencyHandler:
    @classmethod
    def permanently_delete_and_update_dependencies(
        cls, field: Field
    ) -> CachingFieldUpdateCollector:
        """
        Permanently deletes a field and ensures the field dependency graph is
        correctly updated after.
        :param field: The field to permanently delete.
        :return: A collection of the fields which were updated as a result of the
            deletion.
        """

        direct_descendants_edges = _get_direct_descendants_and_break_node(field)

        field.delete()

        updated_fields = CachingFieldUpdateCollector()
        _visit_all_dependencies(
            _field_deleted_visitors(updated_fields),
            starting_edges=direct_descendants_edges,
            field_lookup_cache=updated_fields,
        )
        return updated_fields

    @classmethod
    def trash_and_update_dependencies(
        cls, requesting_user, group, field
    ) -> CachingFieldUpdateCollector:
        """
        Trashes a field and ensures the field dependency graph is correctly updated
        after.

        :param requesting_user: The user who is requesting that this item be trashed.
        :param group: The group the trashed item is in.
        :param field: The field to permanently delete.
        :return: A collection of the fields which were updated as a result of the
            deletion.
        """

        direct_descendants_edges = _get_direct_descendants_and_break_node(field)

        TrashHandler.trash(requesting_user, group, field.table.database, field)

        updated_fields = CachingFieldUpdateCollector()
        updated_fields.add_updated_field(field)
        _visit_all_dependencies(
            _field_deleted_visitors(updated_fields),
            starting_edges=direct_descendants_edges,
            field_lookup_cache=updated_fields,
        )
        return updated_fields

    @classmethod
    def refresh_all_dependant_rows(
        cls, changed_row_id: int, updated_fields: List[Field]
    ):
        """
        Given a single row has had some fields updated this function will go through
        all dependant fields and refresh their row values accordingly.

        :param updated_fields: The list of fields which changed in the row.
        :param changed_row_id: The id of the row which changed.
        """

        updated_fields_collector = CachingFieldUpdateCollector()
        starting_edges = []
        for field in updated_fields:
            starting_edges += _direct_non_broken_dependency_edges(field)

        _visit_all_dependencies(
            [
                BulkMultiTableFormulaFieldRefresher(
                    updated_fields_collector,
                    refresh_row_values=True,
                    recalculate_internal_formulas=False,
                    starting_row_id=changed_row_id,
                ),
            ],
            starting_edges=starting_edges,
            field_lookup_cache=updated_fields_collector,
        )

    @classmethod
    def update_field_dependency_graph_after_field_change(
        cls,
        changed_field: Optional[Field] = None,
        old_changed_field: Optional[Field] = None,
        rename_only: bool = False,
        field_lookup_cache: FieldCache = None,
    ) -> CachingFieldUpdateCollector:
        """
        Will do all required field graph operations after a field has changed in some
        way.

        :param changed_field: The updated/created/restored field instance.
        :param old_changed_field: If there was a previous version of the field this
            should be it.
        :param rename_only: If it is known that the only thing that has changed about
            the field is it's name then set this to True to optimize the resulting
            graph update.
        :param field_lookup_cache: If a field cache has already been made and populated
            provide it here and the field graph will continue to use it.
        :return: A collection of all fields that updated as a result of the field graph
            update.
        :raises CircularFieldDependencyError:
        :raises SelfReferenceFieldDependencyError:
        """

        updated_fields = CachingFieldUpdateCollector(field_lookup_cache)

        if changed_field is not None:
            fixed_some_fields = update_fields_with_broken_references(changed_field)
            if fixed_some_fields:
                rename_only = False

        _visit_all_dependencies(
            _field_changed_visitors(
                changed_field, old_changed_field, rename_only, updated_fields
            ),
            field=changed_field,
            old_field=old_changed_field,
            field_lookup_cache=updated_fields,
        )
        return updated_fields

    @classmethod
    def get_same_table_dependencies(cls, field: Field) -> List[Field]:
        """
        Returns the list of fields that the provided field directly depends on which
        are in the same table.

        :param field: The field to get dependencies for.
        :return: A list of specific field instances.
        """

        node = field.get_node_or_none()
        if node is None:
            return []
        direct_field_dependencies = []
        edges_to_real_fields = (
            FieldDependencyEdge.objects.filter(child=node, parent__field__isnull=False)
            .select_related("parent__field")
            .all()
        )
        for dep in edges_to_real_fields:
            if dep.via is not None and dep.via != field:
                # The dependency points at a field in another table via the dep.via
                # field in this table, so we depend on the via but not the parent
                # field.
                direct_field_dependencies.append(dep.via.specific)
            else:
                direct_field_dependencies.append(dep.parent.field.specific)
        return direct_field_dependencies

    @classmethod
    def check_for_circular_references(
        cls, field: Field, field_lookup_cache: Optional[FieldCache] = None
    ):
        """
        Checks if the provided field instance in its current state will result in
        any circular or self references, if so it will raise. Will not make any changes
        to the field graph.

        :param field: The field to check for circular/self references on.
        :type field: Field
        :param field_lookup_cache: A cache which will be used to lookup the actual
            fields referenced by any provided field dependencies.
        :raises CircularFieldDependencyError:
        :raises SelfReferenceFieldDependencyError:
        """

        if field_lookup_cache is None:
            field_lookup_cache = FieldCache()

        with transaction.atomic():
            _rebuild_field_dependencies(field, field_lookup_cache)
            # The field graph might have been successfully changed, ensure we undo
            # these changes as we only want to check and not save.
            transaction.set_rollback(True)

    @classmethod
    def rebuild_graph(cls, fields: List[Field]):
        """
        Rebuilds the graph structure for the provided fields but does not do any post
        graph setup processing (e.g. refreshing formula or lookup field values).

        :param fields: An iterable of fields to rebuild their field dependency graph
            for.
        :raises CircularFieldDependencyError:
        :raises SelfReferenceFieldDependencyError:
        """

        updated_fields = CachingFieldUpdateCollector()
        visitors = [
            FieldDependencyRebuildingVisitor(updated_fields, rebuild_all_children=True),
            BulkMultiTableFormulaFieldRefresher(
                updated_fields,
                recalculate_internal_formulas=True,
                refresh_row_values=False,
                # The tables might not yet exist and hence we can't do any operations
                # on the fields actual table like recreating the field.
                recreate_database_columns=False,
            ),
        ]

        for field in fields:
            _visit_all_dependencies(
                visitors, field=field, field_lookup_cache=updated_fields
            )
