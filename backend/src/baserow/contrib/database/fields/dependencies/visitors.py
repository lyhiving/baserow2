import abc
from typing import List, Union

from baserow.contrib.database.fields.dependencies.update_collector import (
    CachingFieldUpdateCollector,
)


class FieldGraphDependencyVisitor(abc.ABC):
    """
    A visitor which can be used to perform relevant field or row changes when a field
    or row with dependencies in Baserow changes.
    """

    def __init__(self, updated_fields_collector: CachingFieldUpdateCollector):
        self.updated_fields_collector = updated_fields_collector

    @abc.abstractmethod
    def visit_field_dependency(
        self,
        child_field,
        parent_field,
        via_field,
        path_to_starting_field: List[str],
    ):
        """
        Called on each row/field dependency.

        :param child_field: The field which depends on the parent_field
        :param parent_field: The field which is depended on by the child_field.
        :param via_field: If this dependency is via another field this will be that
            field.
        :param path_to_starting_field: If there was a single field which triggered this
            graph update this will be a list of column names leading back to the
            table containing that field. These column names are the m2m relations which
            connect the current child_field back through the dependency graph to the
            starting field.
        :return: True if this visitor also wants to visit all the dependencies of the
            child_field, False otherwise.
        """

        pass

    @abc.abstractmethod
    def visit_starting_field(
        self,
        starting_field,
        old_starting_field,
    ):
        """
        If a field graph update is starting from a specific changed field this function
        will be called with that field.

        :param starting_field: The field whose change is triggering a field graph
            update.
        :param old_starting_field: If the field was updated this will be its instance
            containing values prior to the update.
        """

        pass

    def after_graph_visit(self):
        """
        Called at the end of any graph visiting for any cleanup / final steps to occur.
        """

        pass

    def only_for_specific_field_types(self) -> Union[bool, List[str]]:
        """
        Override this if your visitor only wants to visit dependant fields of a
        particular field type. Return a list of the field types you want to visit.
        """

        return False

    def accepts(self, field_type):
        specific_types = self.only_for_specific_field_types()
        return not specific_types or field_type.type in specific_types


class FieldGraphRenamingVisitor(FieldGraphDependencyVisitor):
    def __init__(
        self,
        updated_fields_collector: CachingFieldUpdateCollector,
        old_name: str,
        new_name: str,
    ):
        super().__init__(updated_fields_collector)
        self.old_name = old_name
        self.new_name = new_name

    def visit_starting_field(
        self,
        starting_field,
        old_starting_field,
    ):
        # The starting field has been renamed so it has been updated
        self.updated_fields_collector.add_updated_field(starting_field)

    def visit_field_dependency(
        self,
        child_field,
        parent_field,
        via_field,
        path_to_starting_field: List[str],
    ):
        from baserow.contrib.database.fields.registries import field_type_registry

        child_field_type = field_type_registry.get_by_model(child_field)
        child_field_type.after_dependency_rename(
            child_field,
            self.old_name,
            self.new_name,
            via_field,
        )
        self.updated_fields_collector.add_updated_field(child_field)
        # A rename of a field can only affect its direct dependencies, return False
        # so we don't bother visiting child_field's children as they can't
        # have changed.
        return False
