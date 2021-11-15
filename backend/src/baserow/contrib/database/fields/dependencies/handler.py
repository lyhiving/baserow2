from typing import Optional, List

from baserow.contrib.database.fields.dependencies.depedency_rebuilder import (
    rebuild_field_dependencies,
    update_fields_with_broken_references,
    check_for_circular,
)
from baserow.contrib.database.fields.dependencies.models import FieldDependency
from baserow.contrib.database.fields.dependencies.update_collector import (
    CachingFieldUpdateCollector,
)
from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.fields.models import Field, LinkRowField
from baserow.core.trash.handler import TrashHandler


def _dependant_fields(field_or_fields, field_cache, via_path=None):
    if via_path is None:
        via_path = []
    if not isinstance(field_or_fields, list):
        fields = [field_or_fields]
    else:
        fields = field_or_fields
    from baserow.contrib.database.fields.registries import field_type_registry

    for field in fields:
        for field_dependency in field.dependants.select_related("dependant").all():
            dependant_field = field_cache.lookup_specific(field_dependency.dependant)
            dependant_field_type = field_type_registry.get_by_model(dependant_field)
            if field_dependency.via is not None:
                new_via_path = via_path + [field_dependency.via]
            else:
                new_via_path = via_path
            yield dependant_field, dependant_field_type, new_via_path


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

        field_update_collector = CachingFieldUpdateCollector()
        dependant_fields = list(_dependant_fields(field, field_update_collector))
        field.dependants.update(dependency=None, broken_reference_field_name=field.name)

        field.delete()

        for (
            dependant_field,
            dependant_field_type,
            via_path,
        ) in dependant_fields:
            dependant_field_type.field_dependency_deleted(
                dependant_field, field, via_path, field_update_collector
            )
        field_update_collector.apply_updates()

        return field_update_collector

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

        field_update_collector = CachingFieldUpdateCollector()
        dependant_fields = list(_dependant_fields(field, field_update_collector))
        field.dependants.update(dependency=None, broken_reference_field_name=field.name)
        if isinstance(field, LinkRowField):
            FieldDependency.objects.filter(via=field).delete()

        TrashHandler.trash(requesting_user, group, field.table.database, field)

        field_update_collector.add_updated_field(field)
        for (
            dependant_field,
            dependant_field_type,
            path_to_dependant,
        ) in dependant_fields:
            dependant_field_type.field_dependency_deleted(
                dependant_field,
                field,
                path_to_dependant,
                field_update_collector,
            )
        field_update_collector.apply_updates()

        return field_update_collector

    @classmethod
    def update_dependants_after_field_updated(
        cls,
        updated_field,
        old_updated_field,
        field_cache=None,
        update_collector=None,
        via_path=None,
        apply_updates=False,
    ):
        if update_collector is None:
            update_collector = CachingFieldUpdateCollector(field_cache)
        update_fields_with_broken_references(updated_field)
        update_collector.add_updated_field(updated_field)
        cls.rebuild_dependencies(updated_field, update_collector)
        for (
            dependant_field,
            dependant_field_type,
            path_to_dependant,
        ) in _dependant_fields(updated_field, update_collector, via_path):
            dependant_field_type.field_dependency_updated(
                dependant_field,
                updated_field,
                old_updated_field,
                path_to_dependant,
                update_collector,
            )
        if apply_updates:
            update_collector.apply_updates()
        return update_collector

    @classmethod
    def update_dependants_after_field_created(cls, created_field, field_cache):
        field_update_collector = CachingFieldUpdateCollector(field_cache)
        update_fields_with_broken_references(created_field)
        field_update_collector.add_updated_field(created_field)
        cls.rebuild_dependencies(created_field, field_update_collector)
        for (
            dependant_field,
            dependant_field_type,
            path_to_dependant,
        ) in _dependant_fields(created_field, field_update_collector):
            dependant_field_type.field_dependency_created(
                dependant_field,
                created_field,
                path_to_dependant,
                field_update_collector,
            )
        field_update_collector.apply_updates()
        return field_update_collector

    @classmethod
    def get_same_table_dependencies(cls, field: Field) -> List[Field]:
        """
        Returns the list of fields that the provided field directly depends on which
        are in the same table.

        :param field: The field to get dependencies for.
        :return: A list of specific field instances.
        """

        # TODO does using the lookup cache make sense here?
        return [
            dep.specific
            for dep in field.field_dependencies.filter(table=field.table).all()
        ]

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
    def update_dependant_rows_after_row_update(
        cls,
        row,
        updated_fields,
        via_path=None,
        field_update_collector=None,
        apply_updates=False,
    ):

        if field_update_collector is None:
            field_update_collector = CachingFieldUpdateCollector(starting_row_id=row.id)

        if via_path is None:
            via_path = []
        for updated_field, field_type, path in _dependant_fields(
            updated_fields, field_update_collector, via_path
        ):
            field_type.row_of_dependency_updated(
                updated_field, row, field_update_collector, path
            )
        if apply_updates:
            field_update_collector.apply_updates()
        return field_update_collector

    @classmethod
    def update_dependant_rows_after_row_created(cls, row, updated_fields):
        field_update_collector = CachingFieldUpdateCollector(starting_row_id=row.id)
        for updated_field, field_type, path in _dependant_fields(
            updated_fields, field_update_collector
        ):
            field_type.row_of_dependency_created(
                updated_field, row, field_update_collector, path
            )
        field_update_collector.apply_updates()
        return field_update_collector

    @classmethod
    def update_dependant_rows_after_row_deleted(cls, row, updated_fields):
        field_update_collector = CachingFieldUpdateCollector(starting_row_id=row.id)
        for updated_field, field_type, path in _dependant_fields(
            updated_fields, field_update_collector
        ):
            field_type.row_of_dependency_deleted(
                updated_field, row, field_update_collector, path
            )
        field_update_collector.apply_updates()
        return field_update_collector
