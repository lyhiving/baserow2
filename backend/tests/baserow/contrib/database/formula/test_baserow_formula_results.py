import sys

import pytest
from django.conf import settings
from django.urls import reverse

from baserow.contrib.database.fields.models import FormulaField

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
        "The formula failed to map to a valid formula due to: an embedded "
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
    ("'a' + 2", "ERROR_COMPILING_FORMULA", None),
    ("CONCAT('a',2)", "ERROR_COMPILING_FORMULA", None),
    ("CONCAT(1,2)", "ERROR_COMPILING_FORMULA", None),
    ("UPPER(1,2)", "ERROR_PARSING_FORMULA", None),
    ("UPPER(1)", "ERROR_COMPILING_FORMULA", None),
    ("LOWER(1,2)", "ERROR_PARSING_FORMULA", None),
    ("LOWER(1)", "ERROR_COMPILING_FORMULA", None),
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
