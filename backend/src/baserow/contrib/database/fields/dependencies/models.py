from django.conf import settings
from django.db import models


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
    broken_reference_field_name = models.TextField(null=True, blank=True, db_index=True)

    def __str__(self):
        if self.via is not None:
            return (
                f"{self.dependant} depends via field {self.via.name}:{self.via.id} on"
                f" {self.dependency})"
            )
        else:
            return f"{self.dependant} depends on {self.dependency})"


def will_cause_circular_dep(from_field, to_field):
    return from_field.id in get_all_field_dependencies(to_field)


def get_all_field_dependencies(field):
    from baserow.contrib.database.fields.models import Field

    # TODO include copyright notice from dag
    query_parameters = {
        "pk": field.pk,
        "max_depth": settings.MAX_FIELD_REFERENCE_DEPTH,
    }
    relationship_table = FieldDependency._meta.db_table
    pk_name = "id"
    pks = Field.objects.raw(
        f"""
        WITH RECURSIVE traverse({pk_name}, depth) AS (
            SELECT first.dependency_id, 1
                FROM {relationship_table} AS first
                LEFT OUTER JOIN {relationship_table} AS second
                ON first.dependency_id = second.dependant_id
            WHERE first.dependant_id = %(pk)s
        UNION
            SELECT DISTINCT dependency_id, traverse.depth + 1
                FROM traverse
                INNER JOIN {relationship_table}
                ON {relationship_table}.dependant_id = traverse.{pk_name}
            WHERE 1 = 1
        )
        SELECT {pk_name} FROM traverse
        WHERE depth <= %(max_depth)s
        GROUP BY {pk_name}
        ORDER BY MAX(depth) DESC, {pk_name} ASC
        """,
        query_parameters,
    )
    return {item.pk for item in pks}
