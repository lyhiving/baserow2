from django.conf import settings
from django.db import models
from django.db.models import When, Case


class FieldDependency(models.Model):
    """
    A FieldDependency represents a dependency between two Fields or a single Field
    depending on a field name which doesn't exist as a field yet.
    """

    dependant = models.ForeignKey(
        "database.Field",
        on_delete=models.CASCADE,
        related_name="dependencies",
    )
    dependency = models.ForeignKey(
        "database.Field",
        on_delete=models.CASCADE,
        related_name="dependants",
        null=True,
        blank=True,
    )
    # The link row field that the dependant depends on the dependency via.
    via = models.ForeignKey(
        "database.LinkRowField",
        on_delete=models.CASCADE,
        related_name="vias",
        null=True,
        blank=True,
    )
    broken_reference_field_name = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.via is not None:
            return (
                f"{self.dependant} depends via field {self.via.name}:{self.via.id} on"
                f" {self.dependency})"
            )
        else:
            return f"{self.dependant} depends on {self.dependency})"


def _ordered_filter(queryset, field_names, values):
    """
    Filters the provided queryset for 'field_name__in values' for each given field_name in [field_names]
    orders results in the same order as provided values

        For instance
            _ordered_filter(self.__class__.objects, "pk", pks)
        returns a queryset of the current class, with instances where the 'pk' field matches an pk in pks

    """

    if not isinstance(field_names, list):
        field_names = [field_names]
    case = []
    for pos, value in enumerate(values):
        when_condition = {field_names[0]: value, "then": pos}
        case.append(When(**when_condition))
    order_by = Case(*case)
    filter_condition = {field_name + "__in": values for field_name in field_names}
    return queryset.filter(**filter_condition).order_by(order_by)


def will_cause_circular_dep(from_field, to_field):
    return from_field in get_all_field_dependencies(to_field)


def get_all_field_dependencies(field):
    from baserow.contrib.database.fields.models import Field

    # TODO include copyright notice from dag
    query_parameters = {
        "pk": field.pk,
        "max_depth": settings.MAX_FIELD_REFERENCE_DEPTH,
    }
    relationship_table = FieldDependency._meta.db_table
    pk_name = field.get_pk_name()
    pks = Field.objects.raw(
        f"""
        WITH RECURSIVE traverse({pk_name}, depth) AS (
            SELECT first.parent_id, 1
                FROM {relationship_table} AS first
                LEFT OUTER JOIN {relationship_table} AS second
                ON first.parent_id = second.child_id
            WHERE first.child_id = %(pk)s
        UNION
            SELECT DISTINCT parent_id, traverse.depth + 1
                FROM traverse
                INNER JOIN {relationship_table}
                ON {relationship_table}.child_id = traverse.{pk_name}
            WHERE 1 = 1
        )
        SELECT {pk_name} FROM traverse
        WHERE depth <= %(max_depth)s
        GROUP BY {pk_name}
        ORDER BY MAX(depth) DESC, {pk_name} ASC
        """,
        query_parameters,
    )
    return _ordered_filter(Field.objects, "pk", pks)
