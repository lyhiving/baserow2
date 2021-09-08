import sys

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from baserow.contrib.database.fields.models import FormulaField
from baserow.core.trash.handler import TrashHandler

VALID_FORMULA_TESTS = [
    ("'test'", "test"),
    ("UPPER('test')", "TEST"),
    ("LOWER('TEST')", "test"),
    ("LOWER(UPPER('test'))", "test"),
    ("LOWER(UPPER('test'))", "test"),
    ("CONCAT('test', ' ', 'works')", "test works"),
    ("CONCAT('test', ' ', UPPER('works'))", "test WORKS"),
    (
        "UPPER(" * 100 + "'test'" + ")" * 100,
        "TEST",
    ),
    (
        "UPPER('" + "t" * settings.MAX_FORMULA_STRING_LENGTH + "')",
        "T" * settings.MAX_FORMULA_STRING_LENGTH,
    ),
    ("'https://उदाहरण.परीक्षा'", "https://उदाहरण.परीक्षा"),
    ("UPPER('https://उदाहरण.परीक्षा')", "HTTPS://उदाहरण.परीक्षा"),
    ("CONCAT('https://उदाहरण.परीक्षा', '/api')", "https://उदाहरण.परीक्षा/api"),
    ("LOWER('HTTPS://उदाहरण.परीक्षा')", "https://उदाहरण.परीक्षा"),
    ("CONCAT('\ntest', '\n')", "\ntest\n"),
    ("1+1", "2"),
    ("1/0", "NaN"),
    ("10/3", "3.33333"),
    ("(10+2)/3", "4.00000"),
    ("CONCAT(1,2)", "12"),
    ("CONCAT('a',2)", "a2"),
]


def a_test_case(name, starting_table_setup, formula_info, expectation):
    return name, starting_table_setup, formula_info, expectation


def given_a_table(columns, rows):
    return columns, rows


def when_a_formula_field_is_added(formula):
    return formula


def when_multiple_formula_fields_are_added(formulas):
    return formulas


def then_expect_the_rows_to_be(rows):
    return rows


COMPLEX_VALID_TESTS = [
    a_test_case(
        "Can reference and add to a integer column",
        given_a_table(columns=[("number", "number")], rows=[[1], [2], [None]]),
        when_a_formula_field_is_added("field('number')+1"),
        then_expect_the_rows_to_be([["1", "2"], ["2", "3"], [None, None]]),
    ),
    a_test_case(
        "Can reference and add to a integer column",
        given_a_table(columns=[("number", "number")], rows=[[1], [2], [None]]),
        when_multiple_formula_fields_are_added(
            [("formula_1", "field('number')+1"), "field('formula_1')+1"]
        ),
        then_expect_the_rows_to_be(
            [["1", "2", "3"], ["2", "3", "4"], [None, None, None]]
        ),
    ),
]
INVALID_FORMULA_TESTS = [
    (
        "test",
        "ERROR_PARSING_FORMULA",
        (
            "The formula failed to parse due to: Invalid syntax at line 1, col 4: "
            "mismatched input 'the end of the formula' expecting '('."
        ),
    ),
    (
        "UPPER(" * (sys.getrecursionlimit())
        + "'test'"
        + ")" * (sys.getrecursionlimit()),
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: it exceeded the maximum formula size.",
    ),
    (
        "CONCAT(" + ",".join(["'test'"] * 5000) + ")",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: it exceeded the maximum formula size.",
    ),
    (
        "UPPER('" + "t" * (settings.MAX_FORMULA_STRING_LENGTH + 1) + "')",
        "ERROR_MAPPING_FORMULA",
        "The formula is invalid because an embedded "
        f"string in the formula over the maximum length of "
        f"{settings.MAX_FORMULA_STRING_LENGTH} .",
    ),
    (
        "CONCAT()",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function concat. It excepts more than 1 arguments but "
        "instead 0 were given.",
    ),
    (
        "CONCAT('a')",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function concat. It excepts more than 1 arguments but "
        "instead 1 were given.",
    ),
    (
        "UPPER()",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function upper. It excepts exactly 1 arguments but "
        "instead 0 were given.",
    ),
    (
        "LOWER()",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function lower. It excepts exactly 1 arguments but "
        "instead 0 were given.",
    ),
    (
        "UPPER('a','a')",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function upper. It excepts exactly 1 arguments but "
        "instead 2 were given.",
    ),
    (
        "LOWER('a','a')",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function lower. It excepts exactly 1 arguments but "
        "instead 2 were given.",
    ),
    (
        "LOWER('a', CONCAT())",
        "ERROR_PARSING_FORMULA",
        "The formula failed to parse due to: An invalid number of arguments were "
        "provided to the function lower. It excepts exactly 1 arguments but "
        "instead 2 were given.",
    ),
    ("'a' + 2", "ERROR_MAPPING_FORMULA", None),
    ("UPPER(1,2)", "ERROR_PARSING_FORMULA", None),
    ("UPPER(1)", "ERROR_MAPPING_FORMULA", None),
    ("LOWER(1,2)", "ERROR_PARSING_FORMULA", None),
    ("LOWER(1)", "ERROR_MAPPING_FORMULA", None),
    ("10/LOWER(1)", "ERROR_MAPPING_FORMULA", None),
    ("'t'/1", "ERROR_MAPPING_FORMULA", None),
    ("1/'t'", "ERROR_MAPPING_FORMULA", None),
]


@pytest.mark.parametrize("test_input,expected", VALID_FORMULA_TESTS)
@pytest.mark.django_db
def test_valid_formulas(test_input, expected, data_fixture, api_client):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula2", "type": "formula", "formula": test_input},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200, response.json()
    field_id = response.json()["id"]
    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{field_id}"] == expected


@pytest.mark.parametrize("name,table_setup,formula,expected", COMPLEX_VALID_TESTS)
@pytest.mark.django_db
def test_valid_complex_formulas(
    name,
    table_setup,
    formula,
    expected,
    data_fixture,
    api_client,
    django_assert_num_queries,
):
    user, token = data_fixture.create_user_and_token()
    table, fields, rows = data_fixture.build_table(
        columns=table_setup[0], rows=table_setup[1], user=user
    )
    if not isinstance(formula, list):
        formula = [formula]
    formula_field_ids = []
    j = 0
    for f in formula:
        if not isinstance(f, tuple):
            f = f"baserow_formula_{j}", f
            j += 1
        response = api_client.post(
            reverse("api:database:fields:list", kwargs={"table_id": table.id}),
            {"name": f[0], "type": "formula", "formula": f[1]},
            format="json",
            HTTP_AUTHORIZATION=f"JWT {token}",
        )
        assert response.status_code == 200, response.json()
        formula_field_ids.append(response.json()["id"])
    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == len(table_setup[1]) + 1
    i = 0
    for row in expected:
        k = 0
        for field in fields:
            assert response_json["results"][i][f"field_{field.id}"] == row[k]
            k += 1
        for f_id in formula_field_ids:
            assert response_json["results"][i][f"field_{f_id}"] == row[k]
            k += 1
        i += 1


@pytest.mark.parametrize("test_input,error,detail", INVALID_FORMULA_TESTS)
@pytest.mark.django_db
def test_invalid_formulas(test_input, error, detail, data_fixture, api_client):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula2", "type": "formula", "formula": test_input},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["error"] == error
    if detail:
        assert response_json["detail"] == detail

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200
    assert response.json() == []
    assert FormulaField.objects.count() == 0


@pytest.mark.django_db
def test_altering_value_of_referenced_field(
    data_fixture, api_client, django_assert_num_queries
):
    test_input = "field('number')+1"
    expected = "2"
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "number", "type": "number", "number_type": "INTEGER"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200, response.json()
    number_field_id = response.json()["id"]
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula2", "type": "formula", "formula": test_input},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200, response.json()
    formula_field_id = response.json()["id"]
    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {f"field_{number_field_id}": 1},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    row_id = response.json()["id"]
    assert response.status_code == 200, response.json()
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == expected

    response = api_client.patch(
        reverse(
            "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_id}
        ),
        {f"field_{number_field_id}": 2},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200, response.json()

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "3"


@pytest.mark.django_db
def test_changing_type_of_reference_field_to_invalid_one_for_formula(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        {"type": "boolean"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "argument 0 invalid" in response_json[1]["error"]


@pytest.mark.django_db
def test_changing_name_of_referenced_field_by_formula(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        {"name": "new_name"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"


@pytest.mark.django_db
def test_trashing_child_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.delete(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "Field number is deleted" in response_json[0]["error"]


@pytest.mark.django_db
def test_perm_deleting_child_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    number_field_id = fields[0].id
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    TrashHandler.permanently_delete(fields[0])

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "Field number is deleted" in response_json[0]["error"]


@pytest.mark.django_db
def test_trashing_restoring_child_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.delete(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "Field number is deleted" in response_json[0]["error"]
    assert response_json[0]["formula"] == "field('number')+1"

    response = api_client.patch(
        reverse("api:trash:restore"),
        {
            "trash_item_type": "field",
            "trash_item_id": fields[0].id,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_204_NO_CONTENT

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert response_json[1]["error"] is None
    assert response_json[1]["formula"] == f"field_by_id({fields[0].id})+1"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"


@pytest.mark.django_db
def test_trashing_renaming_child_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number"), ("number2", "number")], rows=[[1, 2]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.delete(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "Field number is deleted" in response_json[1]["error"]
    assert response_json[1]["formula"] == "field('number')+1"

    # We rename the other field to fit into the formula slot
    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": fields[1].id}),
        {"name": "number"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert response_json[1]["error"] is None
    assert response_json[1]["formula"] == f"field_by_id({fields[1].id})+1"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "3"


@pytest.mark.django_db
def test_trashing_creating_child_field(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[[1]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('number')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] == "2"

    response = api_client.delete(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert "Field number is deleted" in response_json[0]["error"]
    assert response_json[0]["formula"] == "field('number')+1"

    # We create the another field to fit into the formula slot
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "number", "type": "number"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    new_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:fields:item", kwargs={"field_id": formula_field_id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    assert response_json["error"] is None
    assert response_json["formula"] == f"field_by_id({new_field_id})+1"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 1
    assert response_json["results"][0][f"field_{formula_field_id}"] is None


@pytest.mark.django_db
def test_cant_make_self_reference(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "field('Formula')+1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json == {
        "detail": "The formula is invalid because a formula field cannot reference "
        "itself.",
        "error": "ERROR_MAPPING_FORMULA",
    }


@pytest.mark.django_db
def test_cant_make_circular_reference(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula", "type": "formula", "formula": "1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK
    first_formula_field_id = response.json()["id"]

    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula2", "type": "formula", "formula": "field('Formula')"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json

    response = api_client.patch(
        reverse(
            "api:database:fields:item", kwargs={"field_id": first_formula_field_id}
        ),
        {"name": "Formula", "type": "formula", "formula": "field('Formula2')"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json == {
        "detail": "The formula is invalid because a formula field cannot result in a "
        "circular reference, detected a circular reference chain of "
        "Formula->Formula2->Formula.",
        "error": "ERROR_MAPPING_FORMULA",
    }


@pytest.mark.django_db
def test_changing_type_of_reference_field_to_valid_one_for_formula(
    api_client, data_fixture
):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("text", "text")], rows=[["1"], ["not a number"]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {
            "name": "Formula",
            "type": "formula",
            "formula": "concat(field('text'),'test')",
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "1test"
    assert (
        response_json["results"][1][f"field_{formula_field_id}"] == "not a numbertest"
    )

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        {"type": "number"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "1test"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "test"


@pytest.mark.django_db
def test_can_set_number_of_decimal_places(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("number", "number")], rows=[["1"], ["2"]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {
            "name": "Formula",
            "type": "formula",
            "formula": "1/4",
            "number_type": "DECIMAL",
            "number_decimal_places": 5,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "0.25000"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "0.25000"

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": formula_field_id}),
        {
            "name": "Formula",
            "type": "formula",
            "formula": "1/4",
            "number_type": "DECIMAL",
            "number_decimal_places": 2,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "0.25"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "0.25"

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": formula_field_id}),
        {
            "name": "Formula",
            "type": "text",
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "0.25"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "0.25"


@pytest.mark.django_db
def test_altering_type_of_underlying_causes_type_update(api_client, data_fixture):
    user, token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table, fields, rows = data_fixture.build_table(
        columns=[("text", "text")], rows=[["1"], [None]], user=user
    )
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {
            "name": "Formula",
            "type": "formula",
            "formula": "field('text')",
            "text_default": "default",
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json
    formula_field_id = response_json["id"]

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "1"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "default"

    response = api_client.patch(
        reverse("api:database:fields:item", kwargs={"field_id": fields[0].id}),
        {
            "name": "text",
            "type": "number",
            "number_type": "DECIMAL",
            "number_decimal_places": 2,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK, response_json

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    response_json = response.json()
    assert response_json["count"] == 2
    assert response_json["results"][0][f"field_{formula_field_id}"] == "1.00"
    assert response_json["results"][1][f"field_{formula_field_id}"] == "0.00"
