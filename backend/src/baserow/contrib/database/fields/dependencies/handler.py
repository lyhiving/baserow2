from typing import Optional, List, Iterable

from django.db import transaction

from baserow.contrib.database.fields.dependencies.depedency_rebuilder import (
    FieldDependencyRebuildingVisitor,
    rebuild_field_dependencies,
    update_fields_with_broken_references,
    check_for_circular,
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
from baserow.contrib.database.formula import (
    BulkMultiTableFormulaFieldRefresher,
)
from baserow.contrib.database.fields.dependencies.models import FieldDependency
from baserow.core.trash.handler import TrashHandler


def _visit_all_dependencies_breadth_first(
    starting_path: List[str],
    starting_dependencies: Iterable[FieldDependency],
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
    │  ├─ D (3 paths, 5 paths)
    │  │
    ├─ C (4)

    This means field D depends on field B and C, and both B and C depend on A.
    If we did instead a depth first traversal we would calculate in this order:
    X<-A, A<-B, B<-D, A<-C which would result in D have incorrect values as it depends
    on C but C had not yet been visited when D was visited.

    :param starting_dependencies: The dependenies to start traversing the field graph.
    :param visitors: The starting visitors which will visit the starting_edges and
        then depending on each visitor will continue or not visiting further edges.
    :param field_lookup_cache: A cache used to lookup fields from the database.
    """

    deps_with_paths = [(e, starting_path) for e in starting_dependencies]
    while len(deps_with_paths) > 0:
        dependency, path = deps_with_paths.pop(0)
        specific_dependant_field = field_lookup_cache.lookup_specific(
            dependency.dependant.field
        )
        if dependency.dependency.field is not None:
            specific_dependency_field = field_lookup_cache.lookup_specific(
                dependency.dependency.field
            )
        else:
            specific_dependency_field = None

        if dependency.via:
            path = [dependency.via.db_column] + path

        field_type = field_type_registry.get_by_model(specific_dependant_field)
        for v in visitors:
            if v.accepts(field_type):
                v.visit_field_dependency(
                    specific_dependant_field,
                    specific_dependency_field,
                    dependency.via,
                    path,
                )
        deps_with_paths += [
            (d, path) for d in specific_dependant_field.dependants.all()
        ]


def _get_direct_descendants_and_break_dependencies(field):
    dependants_qs = field.field_dependants()
    direct_dependants = list(dependants_qs)
    dependants_qs.update(dependency=None, broken_reference_field_name=field.name)
    return direct_dependants


def _visit_all_dependencies(
    visitors: List[FieldGraphDependencyVisitor],
    field: Optional[Field] = None,
    old_field: Optional[Field] = None,
    starting_edges: Optional[List[FieldDependency]] = None,
    field_lookup_cache=None,
):
    if field_lookup_cache is None:
        field_lookup_cache = FieldCache()

    if field is not None:
        field = field_lookup_cache.lookup_specific(field)
        field_type = field_type_registry.get_by_model(field)
        for v in visitors:
            if v.accepts(field_type):
                v.visit_starting_field(field, old_field)

    if starting_edges is None:
        starting_edges = field.field_dependants()

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
    # No need to bother doing any value refreshing/dependency rebuilding if only the
    # name has changed.
    if not rename_only:
        visitors += [
            FieldDependencyRebuildingVisitor(
                updated_fields, rebuild_first_children=True
            ),
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

        direct_descendants = _get_direct_descendants_and_break_dependencies(field)

        field.delete()

        updated_fields = CachingFieldUpdateCollector()
        _visit_all_dependencies(
            _field_deleted_visitors(updated_fields),
            starting_edges=direct_descendants,
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

        direct_descendants_edges = _get_direct_descendants_and_break_dependencies(field)

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
            starting_edges += field.field_dependants()

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
    def update_graph_after_field_updated(
        cls, updated_field, old_updated_field, field_lookup_cache
    ):
        updated_fields = CachingFieldUpdateCollector(field_lookup_cache)
        cls.update_fields_with_broken_references(updated_field)
        cls.rebuild_dependencies(updated_field, updated_fields)
        for dep in updated_field.field_dependants():
            dependant_field = dep.depedant
            dependant_field_type = field_type_registry.get_by_model(dependant_field)
            dependant_field_type.field_dependency_updated(
                dependant_field, updated_field, old_updated_field, updated_fields
            )
        updated_fields.apply_field_updates()
        return updated_fields

    @classmethod
    def update_graph_after_field_created(cls, created_field, field_lookup_cache):
        updated_fields = CachingFieldUpdateCollector(field_lookup_cache)
        cls.update_fields_with_broken_references(created_field)
        cls.rebuild_dependencies(created_field, updated_fields)
        for dep in created_field.field_dependants():
            dependant_field = dep.depedant
            dependant_field_type = field_type_registry.get_by_model(dependant_field)
            dependant_field_type.field_dependency_created(
                dependant_field, created_field, updated_fields
            )
        updated_fields.apply_field_updates()
        return updated_fields

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

        return [dep.dependency.specific for dep in field.field_dependencies(via=False)]

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

        check_for_circular(field, field_lookup_cache)

    @classmethod
    def rebuild_dependencies(cls, field, field_lookup_cache):
        rebuild_field_dependencies(field, field_lookup_cache)

    @classmethod
    def update_fields_with_broken_references(cls, field):
        update_fields_with_broken_references(field)
