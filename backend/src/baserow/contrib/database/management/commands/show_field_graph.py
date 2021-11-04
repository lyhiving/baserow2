import graphviz as graphviz
from django.core.management.base import BaseCommand

from baserow.contrib.database.formula.models import (
    FieldDependencyNode,
    FieldDependencyEdge,
)


class Command(BaseCommand):
    help = "Displays the graph of fields for a database or all of Baserow"

    def handle(self, *args, **options):
        dot = graphviz.Digraph(format="png")
        nodes = FieldDependencyNode.objects
        edges = FieldDependencyEdge.objects
        node_count = 0
        for node in nodes.all():
            if not node.is_island():
                dot.node(str(node.id), str(node))
                node_count += 1
        for edge in edges.all():
            dot.edge(str(edge.child_id), str(edge.parent_id))
        print(f"Generated graph with {node_count} nodes and {edges.count()} edges...")
        dot.render("diagram")
