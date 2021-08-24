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
        "The formula failed to parse due to: it exceeded the maximum nested formula "
        "depth allowed.",
    ),
    (
        "CONCAT(" + ",".join(["'test'"] * 5000) + ")",
        "ERROR_TOO_DEEPLY_NESTED_FORMULA",
        "The formula is too deeply nested.",
    ),
    (
        "UPPER('" + "t" * (settings.MAX_FORMULA_STRING_LENGTH + 1) + "')",
        "ERROR_MAPPING_FORMULA",
        "The formula failed to map to a valid formula due to: an embedded "
        "string in the formula over the maximum length of 10000 .",
    ),
]


@pytest.mark.parametrize("test_input,expected", VALID_FORMULA_TESTS)
@pytest.mark.django_db
def test_formulas(test_input, expected, data_fixture, api_client):
    user, token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    response = api_client.post(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        {"name": "Formula2", "type": "formula", "formula": test_input},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200
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
    assert response_json["detail"] == detail

    response = api_client.get(
        reverse("api:database:fields:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {token}",
    )
    assert response.status_code == 200
    assert response.json() == []
    assert FormulaField.objects.count() == 0
