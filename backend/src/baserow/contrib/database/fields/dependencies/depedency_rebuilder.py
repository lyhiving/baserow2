from typing import Optional, Tuple

from baserow.contrib.database.fields import models as field_models
from baserow.contrib.database.fields.dependencies.exceptions import (
    CircularFieldDependencyError,
    SelfReferenceFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.models import FieldDependency
from baserow.contrib.database.fields.dependencies.models import (
    will_cause_circular_dep,
)
from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.table import models as table_models


def update_fields_with_broken_references(field: "field_models.Field"):
    """
    Checks to see if there are any fields which should now depend on `field` if it's
    name has changed to match a broken reference.

    :param field: The field that has potentially just been renamed.
    :return: True if some fields were found which now depend on field, False otherwise.
    """

    broken_dependencies_fixed_by_fields_name = FieldDependency.objects.filter(
        dependant__table=field.table,
        broken_reference_field_name=field.name,
    )
    updated_deps = []
    for dep in broken_dependencies_fixed_by_fields_name:
        if not will_cause_circular_dep(dep.dependant, field):
            dep.dependency = field
            dep.broken_reference_field_name = None
            updated_deps.append(dep)
    FieldDependency.objects.bulk_update(
        updated_deps, ["dependency", "broken_reference_field_name"]
    )

    return len(updated_deps) > 0


def _add_graph_dependency_raising_if_circular(
    field: "field_models.Field",
    dependency_field_name: str,
    field_lookup_cache: FieldCache,
    via_field_name: Optional[str] = None,
):
    table = field.table
    if via_field_name is None:
        dependency_field = field_lookup_cache.lookup_by_name(
            table, dependency_field_name
        )
        if dependency_field is None:
            FieldDependency.objects.create(
                dependant=field, broken_reference_field_name=dependency_field_name
            )
        else:
            _create_dependency_raising_if_circular(field, dependency_field)
    else:
        _add_dep_with_via(
            field, dependency_field_name, table, via_field_name, field_lookup_cache
        )


def _add_dep_with_via(
    field: "field_models.Field",
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
        FieldDependency.objects.create(
            dependant=field, broken_reference_field_name=via_field_name
        )
    else:
        target_table = via_field.link_row_table
        target_field = field_lookup_cache.lookup_by_name(
            target_table, dependency_field_name
        )
        if target_field is None:
            FieldDependency.objects.create(
                dependant=field,
                broken_reference_field_name=dependency_field_name,
                via=via_field,
            )
        else:
            if field.id != via_field.id:
                # Depend directly on the via field also so if it is renamed or changes
                # we get notified.
                _create_dependency_raising_if_circular(field, via_field)
            _create_dependency_raising_if_circular(
                field, target_field, via_field=via_field
            )


def _create_dependency_raising_if_circular(
    field: "field_models.Field",
    dependency_field: "field_models.Field",
    via_field: Optional["field_models.Field"] = None,
):
    if not will_cause_circular_dep(field, dependency_field):
        FieldDependency.objects.create(
            dependency=dependency_field, dependant=field, via=via_field
        )
    else:
        raise CircularFieldDependencyError()


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


def rebuild_field_dependencies(
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

    from baserow.contrib.database.fields.registries import field_type_registry

    field_type = field_type_registry.get_by_model(field_instance)
    field_dependencies = field_type.get_field_dependencies(
        field_instance, field_lookup_cache
    )
    if field_dependencies is not None:
        FieldDependency.objects.filter(dependant=field_instance).delete()
        for dependency in field_dependencies:
            _add_dependency(field_instance, dependency, field_lookup_cache)


def check_for_circular(
    field_instance,
    field_lookup_cache: FieldCache,
):
    from baserow.contrib.database.fields.registries import field_type_registry

    field_type = field_type_registry.get_by_model(field_instance)
    field_dependencies = field_type.get_field_dependencies(
        field_instance, field_lookup_cache
    )
    if field_dependencies is not None:
        for dependency in field_dependencies:
            if isinstance(dependency, Tuple):
                (
                    via_field_name,
                    dependency,
                ) = dependency
                via_field = field_lookup_cache.lookup_by_name(
                    field_instance.table, via_field_name
                )
                if via_field is not None:
                    dependency_field = field_lookup_cache.lookup_by_name(
                        via_field.link_row_table, dependency
                    )
                else:
                    dependency_field = None
            else:
                dependency_field = field_lookup_cache.lookup_by_name(
                    field_instance.table, dependency
                )

            if field_instance.name == dependency_field.name:
                raise SelfReferenceFieldDependencyError()

            if will_cause_circular_dep(field_instance, dependency_field):
                raise CircularFieldDependencyError()
