from copy import deepcopy

import pytest

from baserow.contrib.database.fields.dependencies.exceptions import (
    SelfReferenceFieldDependencyError,
    CircularFieldDependencyError,
)
from baserow.contrib.database.fields.dependencies.handler import (
    FieldDependencyHandler,
)
from baserow.contrib.database.fields.dependencies.types import FieldDependencies
from baserow.contrib.database.fields.field_types import TextFieldType
from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.formula.models import FieldDependencyNode


class TextFieldTypeButWithDependencies(TextFieldType):
    def get_field_dependencies(
        self, field_instance, field_lookup_cache
    ) -> FieldDependencies:
        return field_instance.dependencies


def given_a_field_which_can_have_dependencies(
    data_fixture, mutable_field_type_registry, starting_dependencies=None, **kwargs
):
    kwargs.setdefault("name", "field_with_deps")
    mutable_field_type_registry.registry["text"] = TextFieldTypeButWithDependencies()
    field = data_fixture.create_text_field(**kwargs)
    if starting_dependencies is not None:
        when_its_dependencies_are_set_to_become(field, starting_dependencies)
        FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    return field


def when_its_dependencies_are_set_to_become(field, dependencies):
    setattr(field, "dependencies", dependencies)


@pytest.mark.django_db
def test_a_field_type_can_define_a_list_of_field_dependencies(
    data_fixture, mutable_field_type_registry
):
    parent_field = data_fixture.create_boolean_field(name="parent")
    field = given_a_field_which_can_have_dependencies(
        data_fixture, mutable_field_type_registry, table=parent_field.table
    )
    when_its_dependencies_are_set_to_become(field, [parent_field.name])
    FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    assert FieldDependencyHandler.get_same_table_dependencies(field) == [parent_field]
    node = field.get_node_or_none()
    # Assert no fields depend on field
    assert node.descendants_tree() == {}
    # Assert that the only field it depends on is parent_field and parent_field has
    # no dependencies as a result.
    assert node.ancestors_tree() == {parent_field.get_node_or_none(): {}}


@pytest.mark.django_db
def test_a_field_with_no_dependencies_ends_up_with_none(
    data_fixture, mutable_field_type_registry
):
    field = given_a_field_which_can_have_dependencies(
        data_fixture, mutable_field_type_registry
    )
    when_its_dependencies_are_set_to_become(field, None)
    FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    assert FieldDependencyHandler.get_same_table_dependencies(field) == []
    node = field.get_node_or_none()
    assert node is None
    assert not FieldDependencyNode.objects.exists()


@pytest.mark.django_db
def test_a_field_with_empty_dependencies_deletes_previous_deps(
    data_fixture, mutable_field_type_registry
):
    parent_field = data_fixture.create_boolean_field(name="parent")
    field = given_a_field_which_can_have_dependencies(
        data_fixture,
        mutable_field_type_registry,
        starting_dependencies=[parent_field.name],
        table=parent_field.table,
    )
    when_its_dependencies_are_set_to_become(field, [])
    FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    assert FieldDependencyHandler.get_same_table_dependencies(field) == []
    node = field.get_node_or_none()
    assert node.descendants_tree() == {}
    assert node.ancestors_tree() == {}


@pytest.mark.django_db
def test_can_create_a_field_with_multiple_dependencies_to_different_fields(
    data_fixture, mutable_field_type_registry
):
    parent_field = data_fixture.create_boolean_field(name="parent")
    parent_field2 = data_fixture.create_boolean_field(
        name="parent2", table=parent_field.table
    )
    field = given_a_field_which_can_have_dependencies(
        data_fixture,
        mutable_field_type_registry,
        table=parent_field.table,
    )
    when_its_dependencies_are_set_to_become(
        field, [parent_field.name, parent_field2.name]
    )

    FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    assert FieldDependencyHandler.get_same_table_dependencies(field) == [
        parent_field,
        parent_field2,
    ]
    node = field.get_node_or_none()
    assert node.descendants_tree() == {}
    assert node.ancestors_tree() == {
        parent_field.get_node_or_none(): {},
        parent_field2.get_node_or_none(): {},
    }


@pytest.mark.django_db
def test_circular_dependencies_raise(data_fixture, mutable_field_type_registry):
    field = given_a_field_which_can_have_dependencies(
        data_fixture,
        mutable_field_type_registry,
    )
    other_field = given_a_field_which_can_have_dependencies(
        data_fixture,
        mutable_field_type_registry,
        name="other_field",
        table=field.table,
        starting_dependencies=[field.name],
    )
    when_its_dependencies_are_set_to_become(field, [other_field.name])

    with pytest.raises(CircularFieldDependencyError):
        FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    with pytest.raises(CircularFieldDependencyError):
        FieldDependencyHandler.check_for_circular_references(field)

    assert FieldDependencyHandler.get_same_table_dependencies(field) == []
    assert FieldDependencyHandler.get_same_table_dependencies(other_field) == [field]

    field_node = field.get_node_or_none()
    assert field_node.descendants_tree() == {other_field.get_node_or_none(): {}}
    assert field_node.ancestors_tree() == {}


@pytest.mark.django_db
def test_self_references_raise(data_fixture, mutable_field_type_registry):
    field = given_a_field_which_can_have_dependencies(
        data_fixture,
        mutable_field_type_registry,
    )
    when_its_dependencies_are_set_to_become(field, [field.name])

    with pytest.raises(SelfReferenceFieldDependencyError):
        FieldDependencyHandler.update_field_dependency_graph_after_field_change(field)
    with pytest.raises(SelfReferenceFieldDependencyError):
        FieldDependencyHandler.check_for_circular_references(field)

    assert FieldDependencyHandler.get_same_table_dependencies(field) == []

    field_node = field.get_node_or_none()
    assert field_node.descendants_tree() == {}
    assert field_node.ancestors_tree() == {}


@pytest.mark.django_db
def test_only_direct_dependencies_are_updated_when_a_rename_happens(
    data_fixture, mutable_field_type_registry
):
    renamed_field = data_fixture.create_text_field(name="a")
    dependant_field = data_fixture.create_formula_field(
        formula=f"field('a')", name="formula", table=renamed_field.table
    )
    other_dependant_field = data_fixture.create_formula_field(
        formula=f"field('a')", name="formula2", table=renamed_field.table
    )
    non_direct_dependant_field = data_fixture.create_formula_field(
        formula=f"field('formula')", name="other", table=renamed_field.table
    )
    FieldDependencyHandler.rebuild_graph(Field.objects.all())

    assert renamed_field.get_node_or_none().descendants_tree() == {
        dependant_field.get_node_or_none(): {
            non_direct_dependant_field.get_node_or_none(): {}
        },
        other_dependant_field.get_node_or_none(): {},
    }
    old_renamed_field = deepcopy(renamed_field)
    renamed_field.name = "b"
    renamed_field.save()
    updated_fields = (
        FieldDependencyHandler.update_field_dependency_graph_after_field_change(
            changed_field=renamed_field,
            old_changed_field=old_renamed_field,
            rename_only=True,
        )
    )
    dependant_field.refresh_from_db()
    other_dependant_field.refresh_from_db()
    assert dependant_field.formula == "field('b')"
    assert other_dependant_field.formula == "field('b')"
    assert updated_fields.field_has_been_updated(renamed_field)
    assert updated_fields.field_has_been_updated(dependant_field)
    assert updated_fields.field_has_been_updated(other_dependant_field)
    assert not updated_fields.field_has_been_updated(non_direct_dependant_field)


@pytest.mark.django_db
def test_a_rename_that_fixes_broken_references(
    data_fixture, mutable_field_type_registry
):
    renamed_field = data_fixture.create_text_field(name="a")
    dependant_field = data_fixture.create_formula_field(
        formula=f"field('a')", name="formula", table=renamed_field.table
    )
    other_dependant_field = data_fixture.create_formula_field(
        formula=f"field('a')", name="formula2", table=renamed_field.table
    )
    non_direct_dependant_field = data_fixture.create_formula_field(
        formula=f"field('formula')", name="other", table=renamed_field.table
    )
    FieldDependencyHandler.rebuild_graph(Field.objects.all())

    assert renamed_field.get_node_or_none().descendants_tree() == {
        dependant_field.get_node_or_none(): {
            non_direct_dependant_field.get_node_or_none(): {}
        },
        other_dependant_field.get_node_or_none(): {},
    }
    old_renamed_field = deepcopy(renamed_field)
    renamed_field.name = "b"
    renamed_field.save()
    updated_fields = (
        FieldDependencyHandler.update_field_dependency_graph_after_field_change(
            changed_field=renamed_field,
            old_changed_field=old_renamed_field,
            rename_only=True,
        )
    )
    dependant_field.refresh_from_db()
    other_dependant_field.refresh_from_db()
    assert dependant_field.formula == "field('b')"
    assert other_dependant_field.formula == "field('b')"
    assert updated_fields.field_has_been_updated(renamed_field)
    assert updated_fields.field_has_been_updated(dependant_field)
    assert updated_fields.field_has_been_updated(other_dependant_field)
    assert not updated_fields.field_has_been_updated(non_direct_dependant_field)
