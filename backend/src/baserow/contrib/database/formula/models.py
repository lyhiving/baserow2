from django.db import models
from django_postgresql_dag.models import edge_factory, node_factory


class FieldDependencyEdge(edge_factory("FieldDependencyNode", concrete=False)):
    """
    A FieldDependencyEdge represents a dependency between two FieldDependencyNodes.

    A field_dependency_edge with child of Field A and parent of Field B means that
    Field A depends on Field B. So to calculate the value of a Field A we first need to
    know the value of Field B etc.
    """

    # If the child field depends on the parent field via another field (think a link row
    # field) then the via attribute will be set to that middle field.
    via = models.ForeignKey(
        "database.Field",
        on_delete=models.CASCADE,
        related_name="vias",
        null=True,
        blank=True,
    )


class FieldDependencyNode(node_factory(FieldDependencyEdge)):
    """
    A FieldDependencyNode represents one of two things:
        1. A real Baserow field which has dependencies to other FieldNodes.
        2. A "broken reference" which is a non existent field with a particular name
           in a particular table.

    The second case is so other real fields still depend on a node when one of their
    dependencies is deleted. This then lets us easily find these fields with broken
    references when a new field is created/renamed/restored to that table with the
    matching name.

    For example:
    1. Field A depends on Field B and so each has a FieldDependencyNode with a
       FieldDependencyEdge connecting them.
    2. Field B is deleted.
    3. As a result Field B's node is updated to now be a "broken reference":
       1. node.table = node.field.table
       1. node.broken_reference_field_name = node.field.name
       1. node.field = null
    4. Field C is created in the same table with the same name that Field B had.
    5. We can now easily query the dependency graph to find any broken reference nodes
       that Field C fixes.
    6. Field C's new node then replaces the old broken reference node and now Field A
       depends on Field C.

    """

    field = models.OneToOneField(
        "database.Field",
        on_delete=models.CASCADE,
        related_name="nodes",
        null=True,
        blank=True,
    )
    broken_reference_field_name = models.TextField(
        null=True,
        blank=True,
    )
    table = models.ForeignKey(
        "Table",
        on_delete=models.CASCADE,
        related_name="nodes",
    )

    def is_broken_reference_with_no_dependencies(self):
        return not self.is_reference_to_real_field() and self.children.count() == 0

    def is_reference_to_real_field(self):
        return self.field is not None
