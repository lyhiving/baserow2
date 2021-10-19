import pytest

from baserow.contrib.database.formula.parser.exceptions import BaserowFormulaSyntaxError
from baserow.contrib.database.formula.parser.update_field_names import (
    update_field_names,
)


def test_replace_single_quoted_field_ref():
    new_formula = update_field_names("field('test')", {"test": "new test"})

    assert new_formula == "field('new test')"


def test_replace_double_quoted_field_ref():
    new_formula = update_field_names('field("test")', {"test": "new test"})

    assert new_formula == 'field("new test")'


def test_replace_field_reference_keeping_whitespace():
    new_formula = update_field_names(" \n\tfield('test')  \n\t", {"test": "new test"})

    assert new_formula == " \n\tfield('new test')  \n\t"


def test_replace_field_reference_keeping_whitespace_and_comments():
    new_formula = update_field_names(
        "//my line comment \n\tfield('test')  /*my block comment*/\n\t",
        {"test": "new " "test"},
    )

    assert (
        new_formula == "//my line comment \n\tfield('new test')  /*my block "
        "comment*/\n\t"
    )


def test_replace_binary_op_keeping_whitespace_and_comments():
    new_formula = update_field_names(
        "//my line comment \n\t1+1  /*my block comment*/\n\t",
        {"test": "new " "test"},
    )

    assert new_formula == "//my line comment \n\t1+1  /*my block " "comment*/\n\t"


def test_replace_function_call_keeping_whitespace_and_comments():
    new_formula = update_field_names(
        "//my line comment \n\tadd( 1\t \t+\t \t1,\nfield('test')\t)  /*my block "
        "comment*/\n\t",
        {"test": "new test"},
    )

    assert (
        new_formula == "//my line comment \n\tadd( 1\t \t+\t \t1,\nfield('new "
        "test')\t)  /*my block comment*/\n\t"
    )


def test_replace_double_quote_field_ref_containing_single_quotes():
    new_formula = update_field_names(
        'field("test with \'")', {"test with '": "new test with ' \\' and \" and \\\""}
    )

    assert new_formula == 'field("new test with \' \\\' and \\" and \\\\"")'


def test_replace_double_quote_field_ref_containing_double_quotes():
    new_formula = update_field_names(
        "field('test with \\'')", {"test with '": "new test with ' \\' and \" and \\\""}
    )

    assert new_formula == "field('new test with \\' \\\\' and \" and \\\"')"


def test_can_replace_multiple_different_field_references():
    new_formula = update_field_names(
        'concat(field("test"), field("test"), field(\'other\'))',
        {"test": "new test", "other": "new other"},
    )

    assert (
        new_formula == 'concat(field("new test"), field("new test"), '
        "field('new other'))"
    )


def test_leaves_unknown_field_references_along():
    new_formula = update_field_names(
        "field('test')",
        {},
    )
    assert new_formula == "field('test')"


def test_raises_with_field_names_for_invalid_syntax():
    _assert_raises("field('test'")
    _assert_raises("field(''''test'")
    _assert_raises("field(test")
    _assert_raises("field(1)")
    _assert_raises("field)")


def _assert_raises(formula):
    with pytest.raises(BaserowFormulaSyntaxError):
        update_field_names(
            formula,
            {
                "test": "new test",
            },
        )


def test_replaces_unknown_field_by_id_with_field():
    new_formula = update_field_names(
        "field_by_id(1)",
        {},
    )
    assert new_formula == "field('unknown field 1')"


def test_replaces_unknown_field_by_id_with_field_multiple():
    new_formula = update_field_names(
        "field_by_id(1)+concat(field('a'), field_by_id(2))",
        {},
    )
    assert (
        new_formula == "field('unknown field 1')+concat(field('a'), field('unknown "
        "field 2'))"
    )


def test_replaces_known_field_by_id():
    new_formula = update_field_names(
        "field_by_id(1)+concat(field('a'), field_by_id(2))",
        field_ids_to_replace_with_name_refs={1: "test", 2: "other_test"},
    )
    assert new_formula == "field('test')+concat(field('a'), field('other_test'))"


def test_replaces_known_field_by_id_single_quotes():
    new_formula = update_field_names(
        "field_by_id(1)",
        field_ids_to_replace_with_name_refs={1: "test with ' '", 2: "other_test"},
    )
    assert new_formula == "field('test with \\' \\'')"


def test_replaces_known_field_by_id_double_quotes():
    new_formula = update_field_names(
        "field_by_id(1)",
        field_ids_to_replace_with_name_refs={1: 'test with " "', 2: "other_test"},
    )
    assert new_formula == "field('test with \" \"')"


def test_replaces_field_with_field_by_id():
    new_formula = update_field_names(
        "field('a')",
        field_names_to_replace_with_id_refs={"a": 1},
    )
    assert new_formula == "field_by_id(1)"


def test_doesnt_replace_unknown_field():
    new_formula = update_field_names(
        "field('b')+concat(field('a'), field('c'))",
        field_names_to_replace_with_id_refs={"a": 1},
    )
    assert new_formula == "field('b')+concat(field_by_id(1), field('c'))"


def test_replaces_field_with_single_quotes_with_id():
    new_formula = update_field_names(
        "field('test with \\' \\'')",
        field_names_to_replace_with_id_refs={"test with ' '": 1, "other_test": 2},
    )
    assert new_formula == "field_by_id(1)"


def test_replaces_field_with_double_quotes_with_id():
    new_formula = update_field_names(
        "field('test with \" \"')",
        field_names_to_replace_with_id_refs={'test with " "': 1, "other_test": 2},
    )
    assert new_formula == "field_by_id(1)"
