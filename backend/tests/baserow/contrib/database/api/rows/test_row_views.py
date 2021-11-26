from decimal import Decimal

import pytest
from django.shortcuts import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.tokens.handler import TokenHandler


@pytest.mark.django_db
def test_list_rows(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    field_1 = data_fixture.create_text_field(name="Name", table=table, primary=True)
    field_2 = data_fixture.create_number_field(name="Price", table=table)
    field_3 = data_fixture.create_text_field()
    field_4 = data_fixture.create_boolean_field(name="InStock", table=table)

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, False, True, True)

    model = table.get_model(attribute_names=True)
    row_1 = model.objects.create(name="Product 1", price=50, order=Decimal("1"))
    row_2 = model.objects.create(name="Product 2/3", price=100, order=Decimal("2"))
    row_3 = model.objects.create(name="Product 3", price=150, order=Decimal("3"))
    row_4 = model.objects.create(name="Last product", price=200, order=Decimal("4"))

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": 999999}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table_2.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    user.is_active = False
    user.save()
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_USER_NOT_ACTIVE"
    user.is_active = True
    user.save()

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_200_OK

    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 4
    assert len(response_json["results"]) == 4
    assert response_json["results"][0]["id"] == row_1.id
    assert response_json["results"][0][f"field_{field_1.id}"] == "Product 1"
    assert response_json["results"][0][f"field_{field_2.id}"] == "50"
    assert response_json["results"][0]["order"] == "1.00000000000000000000"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?include=field_{field_1.id},field_{field_3.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert f"field_{field_1.id}" in response_json["results"][0]
    assert f"field_{field_2.id}" not in response_json["results"][0]
    assert f"field_{field_3.id}" not in response_json["results"][0]

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?exclude=field_{field_1.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert f"field_{field_1.id}" not in response_json["results"][0]
    assert f"field_{field_2.id}" in response_json["results"][0]

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?size=2&page=1", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 4
    assert len(response_json["results"]) == 2
    assert response_json["results"][0]["id"] == row_1.id
    assert response_json["results"][1]["id"] == row_2.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?size=2&page=2", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 4
    assert len(response_json["results"]) == 2
    assert response_json["results"][0]["id"] == row_3.id
    assert response_json["results"][1]["id"] == row_4.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?size=2&page=3", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_INVALID_PAGE"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?size=201", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_PAGE_SIZE_LIMIT"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?search=Product 1", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 1
    assert len(response_json["results"]) == 1
    assert response_json["results"][0]["id"] == row_1.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?search=4", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 1
    assert len(response_json["results"]) == 1
    assert response_json["results"][0]["id"] == row_4.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?search=3", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 2
    assert len(response_json["results"]) == 2
    assert response_json["results"][0]["id"] == row_2.id
    assert response_json["results"][1]["id"] == row_3.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?search=200", format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 1
    assert len(response_json["results"]) == 1
    assert response_json["results"][0]["id"] == row_4.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?order_by=field_999999",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json["error"] == "ERROR_ORDER_BY_FIELD_NOT_FOUND"
    assert response_json["detail"] == (
        "The field field_999999 was not found in the table."
    )

    number_field_type = field_type_registry.get("number")
    old_can_order_by = number_field_type._can_order_by
    number_field_type._can_order_by = False
    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?order_by=-field_{field_2.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json["error"] == "ERROR_ORDER_BY_FIELD_NOT_POSSIBLE"
    assert response_json["detail"] == (
        f"It is not possible to order by field_{field_2.id} because the field type "
        f"number does not support filtering."
    )
    number_field_type._can_order_by = old_can_order_by

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?order_by=-field_{field_2.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 4
    assert len(response_json["results"]) == 4
    assert response_json["results"][0]["id"] == row_4.id
    assert response_json["results"][1]["id"] == row_3.id
    assert response_json["results"][2]["id"] == row_2.id
    assert response_json["results"][3]["id"] == row_1.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [f"filter__field_9999999__contains=last"]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_FILTER_FIELD_NOT_FOUND"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [f"filter__field_{field_4.id}__contains=100"]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_VIEW_FILTER_TYPE_UNSUPPORTED_FIELD"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [f"filter__field_{field_2.id}__INVALID=100"]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_VIEW_FILTER_TYPE_DOES_NOT_EXIST"
    assert response_json["detail"] == "The view filter type INVALID doesn't exist."

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [
        f"filter__field_{field_1.id}__contains=last",
        f"filter__field_{field_2.id}__equal=200",
    ]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 1
    assert len(response_json["results"]) == 1
    assert response_json["results"][0]["id"] == row_4.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [
        f"filter__field_{field_1.id}__contains=last",
        f"filter__field_{field_2.id}__higher_than=110",
        "filter_type=or",
    ]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 2
    assert len(response_json["results"]) == 2
    assert response_json["results"][0]["id"] == row_3.id
    assert response_json["results"][1]["id"] == row_4.id

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    get_params = [
        f"filter__field_{field_1.id}__equal=Product 1",
        f"filter__field_{field_1.id}__equal=Product 3",
        "filter_type=or",
    ]
    response = api_client.get(
        f'{url}?{"&".join(get_params)}',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 2
    assert len(response_json["results"]) == 2
    assert response_json["results"][0]["id"] == row_1.id
    assert response_json["results"][1]["id"] == row_3.id

    row_2.order = Decimal("999")
    row_2.save()
    response = api_client.get(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["count"] == 4
    assert len(response_json["results"]) == 4
    assert response_json["results"][0]["id"] == row_1.id
    assert response_json["results"][1]["id"] == row_3.id
    assert response_json["results"][2]["id"] == row_4.id
    assert response_json["results"][3]["id"] == row_2.id


@pytest.mark.django_db
def test_create_row(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    text_field = data_fixture.create_text_field(
        table=table, order=0, name="Color", text_default="white"
    )
    number_field = data_fixture.create_number_field(
        table=table, order=1, name="Horsepower"
    )
    boolean_field = data_fixture.create_boolean_field(
        table=table, order=2, name="For sale"
    )
    text_field_2 = data_fixture.create_text_field(
        table=table, order=3, name="Description"
    )

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, False, True, True, True)

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": 99999}),
        {f"field_{text_field.id}": "Test 1"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {f"field_{text_field.id}": "Test 1"},
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {f"field_{text_field.id}": "Test 1"},
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table_2.id}),
        {f"field_{text_field.id}": "Green"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.post(
        f"{url}?before=99999",
        {f"field_{text_field.id}": "Green"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {
            f"field_{text_field.id}": "Green",
            f"field_{number_field.id}": -10,
            f"field_{boolean_field.id}": None,
            f"field_{text_field_2.id}": None,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert len(response_json["detail"]) == 2
    assert response_json["detail"][f"field_{number_field.id}"][0]["code"] == "min_value"
    assert response_json["detail"][f"field_{boolean_field.id}"][0]["code"] == "null"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1[f"field_{text_field.id}"] == "white"
    assert not response_json_row_1[f"field_{number_field.id}"]
    assert response_json_row_1[f"field_{boolean_field.id}"] is False
    assert response_json_row_1[f"field_{text_field_2.id}"] is None
    assert response_json_row_1["order"] == "1.00000000000000000000"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {
            f"field_{number_field.id}": None,
            f"field_{boolean_field.id}": False,
            f"field_{text_field_2.id}": "",
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_2 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_2[f"field_{text_field.id}"] == "white"
    assert not response_json_row_2[f"field_{number_field.id}"]
    assert response_json_row_2[f"field_{boolean_field.id}"] is False
    assert response_json_row_2[f"field_{text_field_2.id}"] == ""
    assert response_json_row_2["order"] == "2.00000000000000000000"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {
            f"field_{text_field.id}": "Green",
            f"field_{number_field.id}": 120,
            f"field_{boolean_field.id}": True,
            f"field_{text_field_2.id}": "Not important",
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_3 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_3[f"field_{text_field.id}"] == "Green"
    assert response_json_row_3[f"field_{number_field.id}"] == "120"
    assert response_json_row_3[f"field_{boolean_field.id}"]
    assert response_json_row_3[f"field_{text_field_2.id}"] == "Not important"
    assert response_json_row_3["order"] == "3.00000000000000000000"

    response = api_client.post(
        reverse("api:database:rows:list", kwargs={"table_id": table.id}),
        {
            f"field_{text_field.id}": "Purple",
            f"field_{number_field.id}": 240,
            f"field_{boolean_field.id}": True,
            f"field_{text_field_2.id}": "",
        },
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    response_json_row_4 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_4[f"field_{text_field.id}"] == "Purple"
    assert response_json_row_4[f"field_{number_field.id}"] == "240"
    assert response_json_row_4[f"field_{boolean_field.id}"]
    assert response_json_row_4[f"field_{text_field_2.id}"] == ""
    assert response_json_row_4["order"] == "4.00000000000000000000"

    token.refresh_from_db()
    assert token.handled_calls == 1

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.post(
        f"{url}?before={response_json_row_3['id']}",
        {
            f"field_{text_field.id}": "Red",
            f"field_{number_field.id}": 480,
            f"field_{boolean_field.id}": False,
            f"field_{text_field_2.id}": "",
        },
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    response_json_row_5 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_5[f"field_{text_field.id}"] == "Red"
    assert response_json_row_5[f"field_{number_field.id}"] == "480"
    assert not response_json_row_5[f"field_{boolean_field.id}"]
    assert response_json_row_5[f"field_{text_field_2.id}"] == ""
    assert response_json_row_5["order"] == "2.99999999999999999999"

    token.refresh_from_db()
    assert token.handled_calls == 2

    model = table.get_model()
    assert model.objects.all().count() == 5
    rows = model.objects.all()

    row_1 = rows[0]
    assert row_1.id == response_json_row_1["id"]
    assert getattr(row_1, f"field_{text_field.id}") == "white"
    assert getattr(row_1, f"field_{number_field.id}") is None
    assert getattr(row_1, f"field_{boolean_field.id}") is False
    assert getattr(row_1, f"field_{text_field_2.id}") is None

    row_2 = rows[1]
    assert row_2.id == response_json_row_2["id"]
    assert getattr(row_2, f"field_{text_field.id}") == "white"
    assert getattr(row_2, f"field_{number_field.id}") is None
    assert getattr(row_2, f"field_{boolean_field.id}") is False
    assert getattr(row_2, f"field_{text_field_2.id}") == ""

    row_5 = rows[2]
    assert row_5.id == response_json_row_5["id"]
    assert getattr(row_5, f"field_{text_field.id}") == "Red"
    assert getattr(row_5, f"field_{number_field.id}") == 480
    assert getattr(row_5, f"field_{boolean_field.id}") is False
    assert getattr(row_5, f"field_{text_field_2.id}") == ""

    row_3 = rows[3]
    assert row_3.id == response_json_row_3["id"]
    assert getattr(row_3, f"field_{text_field.id}") == "Green"
    assert getattr(row_3, f"field_{number_field.id}") == 120
    assert getattr(row_3, f"field_{boolean_field.id}") is True
    assert getattr(row_3, f"field_{text_field_2.id}") == "Not important"

    row_4 = rows[4]
    assert row_4.id == response_json_row_4["id"]
    assert getattr(row_4, f"field_{text_field.id}") == "Purple"
    assert getattr(row_4, f"field_{number_field.id}") == 240
    assert getattr(row_4, f"field_{boolean_field.id}") is True
    assert getattr(row_4, f"field_{text_field_2.id}") == ""

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})

    response = api_client.post(
        f"{url}?user_field_names=true",
        {
            f"Color": "Red",
            f"Horsepower": 480,
            f"For Sale": False,
            f"Description": "",
        },
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "Color": "Red",
        "Description": "",
        "For sale": False,
        "Horsepower": "480",
        "id": 6,
        "order": "5.00000000000000000000",
    }

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.post(
        f"{url}?user_field_names=true",
        {
            f"INVALID FIELD NAME": "Red",
            f"Horsepower": 480,
            f"For Sale": False,
            f"Description": "",
        },
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json == {
        "Color": "white",  # Has gone to the default value when not specified.
        "Description": "",
        "For sale": False,
        "Horsepower": "480",
        "id": 7,
        "order": "6.00000000000000000000",
    }


@pytest.mark.django_db
def test_get_row(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    text_field = data_fixture.create_text_field(
        table=table, order=0, name="Color", text_default="white"
    )
    number_field = data_fixture.create_number_field(
        table=table, order=1, name="Horsepower"
    )
    boolean_field = data_fixture.create_boolean_field(
        table=table, order=2, name="For sale"
    )

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, False, True, True)

    model = table.get_model()
    row_1 = model.objects.create(
        **{
            f"field_{text_field.id}": "Green",
            f"field_{number_field.id}": 120,
            f"field_{boolean_field.id}": False,
        }
    )
    row_2 = model.objects.create(
        **{
            f"field_{text_field.id}": "Purple",
            f"field_{number_field.id}": 240,
            f"field_{boolean_field.id}": True,
        }
    )

    url = reverse("api:database:rows:item", kwargs={"table_id": 9999, "row_id": 9999})
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table_2.id, "row_id": row_1.id}
    )
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION="Token abc123")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.get(
        url, format="json", HTTP_AUTHORIZATION=f"Token {wrong_token.key}"
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": 99999}
    )
    response = api_client.get(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.get(url, format="json", HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["id"] == row_1.id
    assert response_json[f"field_{text_field.id}"] == "Green"
    assert response_json[f"field_{number_field.id}"] == "120"
    assert response_json[f"field_{boolean_field.id}"] is False

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_2.id}
    )
    response = api_client.get(
        url, format="json", HTTP_AUTHORIZATION=f"Token {token.key}"
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["id"] == row_2.id
    assert response_json[f"field_{text_field.id}"] == "Purple"
    assert response_json[f"field_{number_field.id}"] == "240"
    assert response_json[f"field_{boolean_field.id}"] is True


@pytest.mark.django_db
def test_update_row(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    text_field = data_fixture.create_text_field(
        table=table, order=0, name="Color", text_default="white"
    )
    number_field = data_fixture.create_number_field(
        table=table, order=1, name="Horsepower"
    )
    boolean_field = data_fixture.create_boolean_field(
        table=table, order=2, name="For sale"
    )

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, True, False, True)

    model = table.get_model()
    row_1 = model.objects.create()
    row_2 = model.objects.create()

    url = reverse("api:database:rows:item", kwargs={"table_id": 9999, "row_id": 9999})
    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table_2.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": 99999}
    )
    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        {
            f"field_{text_field.id}": "Green",
            f"field_{number_field.id}": -10,
            f"field_{boolean_field.id}": None,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert len(response_json["detail"]) == 2
    assert response_json["detail"][f"field_{number_field.id}"][0]["code"] == "min_value"
    assert response_json["detail"][f"field_{boolean_field.id}"][0]["code"] == "null"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        {
            f"field_{text_field.id}": "Green",
            f"field_{number_field.id}": 120,
            f"field_{boolean_field.id}": True,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1["id"] == row_1.id
    assert response_json_row_1[f"field_{text_field.id}"] == "Green"
    assert response_json_row_1[f"field_{number_field.id}"] == "120"
    assert response_json_row_1[f"field_{boolean_field.id}"] is True

    row_1.refresh_from_db()
    assert getattr(row_1, f"field_{text_field.id}") == "Green"
    assert getattr(row_1, f"field_{number_field.id}") == Decimal("120")
    assert getattr(row_1, f"field_{boolean_field.id}") is True

    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Purple"},
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1[f"field_{text_field.id}"] == "Purple"
    assert response_json_row_1[f"field_{number_field.id}"] == "120"
    assert response_json_row_1[f"field_{boolean_field.id}"] is True
    row_1.refresh_from_db()
    assert getattr(row_1, f"field_{text_field.id}") == "Purple"
    assert getattr(row_1, f"field_{number_field.id}") == Decimal("120")
    assert getattr(row_1, f"field_{boolean_field.id}") is True

    response = api_client.patch(
        url,
        {f"field_{text_field.id}": "Orange"},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1[f"field_{text_field.id}"] == "Orange"
    assert response_json_row_1[f"field_{number_field.id}"] == "120"
    assert response_json_row_1[f"field_{boolean_field.id}"] is True
    row_1.refresh_from_db()
    assert getattr(row_1, f"field_{text_field.id}") == "Orange"
    assert getattr(row_1, f"field_{number_field.id}") == 120
    assert getattr(row_1, f"field_{boolean_field.id}") is True

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_2.id}
    )
    response = api_client.patch(
        url,
        {
            f"field_{text_field.id}": "Blue",
            f"field_{number_field.id}": 50,
            f"field_{boolean_field.id}": False,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_2 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_2["id"] == row_2.id
    assert response_json_row_2[f"field_{text_field.id}"] == "Blue"
    assert response_json_row_2[f"field_{number_field.id}"] == "50"
    assert response_json_row_2[f"field_{boolean_field.id}"] is False

    row_2.refresh_from_db()
    assert getattr(row_2, f"field_{text_field.id}") == "Blue"
    assert getattr(row_2, f"field_{number_field.id}") == Decimal("50")
    assert getattr(row_2, f"field_{boolean_field.id}") is False

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_2.id}
    )
    response = api_client.patch(
        url,
        {
            f"field_{text_field.id}": None,
            f"field_{number_field.id}": None,
            f"field_{boolean_field.id}": False,
        },
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_2 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_2["id"] == row_2.id
    assert response_json_row_2[f"field_{text_field.id}"] is None
    assert response_json_row_2[f"field_{number_field.id}"] is None
    assert response_json_row_2[f"field_{boolean_field.id}"] is False

    row_2.refresh_from_db()
    assert getattr(row_2, f"field_{text_field.id}") is None
    assert getattr(row_2, f"field_{number_field.id}") is None
    assert getattr(row_2, f"field_{boolean_field.id}") is False

    table_3 = data_fixture.create_database_table(user=user)
    decimal_field = data_fixture.create_number_field(
        table=table_3,
        order=0,
        name="Price",
        number_type="DECIMAL",
        number_decimal_places=2,
    )
    model_3 = table_3.get_model()
    row_3 = model_3.objects.create()

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table_3.id, "row_id": row_3.id}
    )
    response = api_client.patch(
        url,
        {f"field_{decimal_field.id}": 10.22},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json[f"field_{decimal_field.id}"] == "10.22"
    assert response_json_row_2[f"field_{number_field.id}"] is None
    assert response_json_row_2[f"field_{boolean_field.id}"] is False

    row_3.refresh_from_db()
    assert getattr(row_3, f"field_{decimal_field.id}") == Decimal("10.22")
    assert getattr(row_2, f"field_{number_field.id}") is None
    assert getattr(row_2, f"field_{boolean_field.id}") is False

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table_3.id, "row_id": row_3.id}
    )
    response = api_client.patch(
        f"{url}?user_field_names=true",
        {f"Price": 10.01},
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json[f"Price"] == "10.01"
    assert "Horsepower" not in response_json
    assert "For sale" not in response_json

    row_3.refresh_from_db()
    assert getattr(row_3, f"field_{decimal_field.id}") == Decimal("10.01")
    assert getattr(row_2, f"field_{number_field.id}") is None
    assert getattr(row_2, f"field_{boolean_field.id}") is False


@pytest.mark.django_db
def test_move_row(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, True, False, True)

    handler = RowHandler()
    row_1 = handler.create_row(user=user, table=table)
    row_2 = handler.create_row(user=user, table=table)
    row_3 = handler.create_row(user=user, table=table)

    url = reverse("api:database:rows:move", kwargs={"table_id": 9999, "row_id": 9999})
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table_2.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION="Token abc123",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION=f"Token {wrong_token.key}",
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": 99999}
    )
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        f"{url}?before_id=-1",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        url,
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1["id"] == row_1.id
    assert response_json_row_1["order"] == "4.00000000000000000000"

    row_1.refresh_from_db()
    row_2.refresh_from_db()
    row_3.refresh_from_db()
    assert row_1.order == Decimal("4.00000000000000000000")
    assert row_2.order == Decimal("2.00000000000000000000")
    assert row_3.order == Decimal("3.00000000000000000000")

    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        f"{url}?before_id={row_3.id}",
        format="json",
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
    response_json_row_1 = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json_row_1["id"] == row_1.id
    assert response_json_row_1["order"] == "2.99999999999999999999"

    row_1.refresh_from_db()
    row_2.refresh_from_db()
    row_3.refresh_from_db()
    assert row_1.order == Decimal("2.99999999999999999999")
    assert row_2.order == Decimal("2.00000000000000000000")
    assert row_3.order == Decimal("3.00000000000000000000")

    data_fixture.create_text_field(user=user, table=table, name="New Field")
    url = reverse(
        "api:database:rows:move", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.patch(
        f"{url}?user_field_names=true",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_200_OK
    response_json_row_1 = response.json()
    assert response_json_row_1 == {
        "New Field": None,
        "id": row_1.id,
        "order": "4.00000000000000000000",
    }

    # Make sure that we receive an error message when calling move row
    # with an before_id != int
    url = reverse("api:database:rows:move", kwargs={"table_id": table.id, "row_id": 1})
    response = api_client.patch(
        f"{url}?before_id=wrong_type",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json["error"] == "ERROR_QUERY_PARAMETER_VALIDATION"
    assert response_json["detail"]["before_id"][0]["code"] == "invalid"
    assert (
        response_json["detail"]["before_id"][0]["error"]
        == "A valid integer is required."
    )


@pytest.mark.django_db
def test_delete_row(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token()
    table = data_fixture.create_database_table(user=user)
    table_2 = data_fixture.create_database_table()
    data_fixture.create_text_field(
        table=table, order=0, name="Color", text_default="white"
    )
    data_fixture.create_number_field(table=table, order=1, name="Horsepower")
    data_fixture.create_boolean_field(table=table, order=2, name="For sale")

    token = TokenHandler().create_token(user, table.database.group, "Good")
    wrong_token = TokenHandler().create_token(user, table.database.group, "Wrong")
    TokenHandler().update_token_permissions(user, wrong_token, True, True, True, False)

    model = table.get_model()
    row_1 = model.objects.create()
    row_2 = model.objects.create()
    row_3 = model.objects.create()

    url = reverse("api:database:rows:item", kwargs={"table_id": 9999, "row_id": 9999})
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": 9999}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_ROW_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"Token abc123")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_TOKEN_DOES_NOT_EXIST"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"Token {wrong_token.key}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()["error"] == "ERROR_NO_PERMISSION_TO_TABLE"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table_2.id, "row_id": row_1.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "ERROR_USER_NOT_IN_GROUP"

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == 204

    assert model.objects.count() == 2
    assert model.objects.all()[0].id == row_2.id

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_2.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"JWT {jwt_token}")
    assert response.status_code == 204
    assert model.objects.count() == 1

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_3.id}
    )
    response = api_client.delete(url, HTTP_AUTHORIZATION=f"Token {token.key}")
    assert response.status_code == 204
    assert model.objects.count() == 0


@pytest.mark.django_db
def test_list_rows_with_attribute_names(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)
    table_to_link_with = data_fixture.create_database_table(
        user=user, database=table.database
    )
    data_fixture.create_text_field(
        primary=True,
        name="Primary",
        table=table_to_link_with,
    )
    field_1 = data_fixture.create_text_field(name="Name", table=table, primary=True)
    field_2 = data_fixture.create_number_field(name="Price,", table=table)
    field_3 = data_fixture.create_boolean_field(name='"Name, 2"', table=table)
    link_field = FieldHandler().create_field(
        user, table, "link_row", link_row_table=table_to_link_with, name="Link"
    )

    model = table.get_model()
    row_1 = model.objects.create(
        **{
            f"field_{field_1.id}": "name 1",
            f"field_{field_2.id}": 2,
            f"field_{field_3.id}": False,
        }
    )
    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?user_field_names=true",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            '"Name, 2"': False,
            "Name": "name 1",
            "Price,": "2",
            "id": 1,
            "order": "1.00000000000000000000",
            "Link": [],
        }
    ]

    url = reverse(
        "api:database:rows:item", kwargs={"table_id": table.id, "row_id": row_1.id}
    )
    response = api_client.get(
        f"{url}?user_field_names=true",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json == {
        "id": 1,
        "Name": "name 1",
        '"Name, 2"': False,
        "order": "1.00000000000000000000",
        "Price,": "2",
        "Link": [],
    }

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f'{url}?user_field_names=true&include="\\"Name, 2\\""',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            '"Name, 2"': False,
            "id": 1,
            "order": "1.00000000000000000000",
        }
    ]

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f'{url}?user_field_names=true&exclude="\\"Name, 2\\""',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            "Name": "name 1",
            "Price,": "2",
            "id": 1,
            "order": "1.00000000000000000000",
            "Link": [],
        }
    ]

    model.objects.create(
        **{
            f"field_{field_1.id}": "name 2",
            f"field_{field_2.id}": 1,
            f"field_{field_3.id}": True,
        }
    )

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?user_field_names=true&order_by={link_field.name}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert (
        response_json["detail"]
        == "It is not possible to order by Link because the field type "
        "link_row does not support filtering."
    )

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?user_field_names=true&order_by=Name",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            '"Name, 2"': False,
            "Name": "name 1",
            "Price,": "2",
            "id": 1,
            "order": "1.00000000000000000000",
            "Link": [],
        },
        {
            '"Name, 2"': True,
            "Name": "name 2",
            "Price,": "1",
            "id": 2,
            "order": "1.00000000000000000000",
            "Link": [],
        },
    ]

    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f'{url}?user_field_names=true&order_by="-\\"Name, 2\\""',
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            '"Name, 2"': True,
            "Name": "name 2",
            "Price,": "1",
            "id": 2,
            "order": "1.00000000000000000000",
            "Link": [],
        },
        {
            '"Name, 2"': False,
            "Name": "name 1",
            "Price,": "2",
            "id": 1,
            "order": "1.00000000000000000000",
            "Link": [],
        },
    ]

    # make sure that when user_field_names is not set
    # that a correct error is presented when still using
    # a field names in order_by
    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?order_by={field_1.name}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_ORDER_BY_FIELD_NOT_FOUND"
    assert (
        response_json["detail"]
        == f"The field {field_1.name} was not found in the table."
    )

    # make sure that when user_field_names is false and we provide
    # a field_id string that we get a result.
    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?user_field_names=false&order_by=field_{field_1.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["results"] == [
        {
            "id": 1,
            "order": "1.00000000000000000000",
            f"field_{field_1.id}": "name 1",
            f"field_{field_3.id}": False,
            f"field_{field_2.id}": "2",
            f"field_{link_field.id}": [],
        },
        {
            "id": 2,
            "order": "1.00000000000000000000",
            f"field_{field_1.id}": "name 2",
            f"field_{field_3.id}": True,
            f"field_{field_2.id}": "1",
            f"field_{link_field.id}": [],
        },
    ]

    # make sure that when user_field_names is true and we provide
    # a field_id string that we get an error.
    url = reverse("api:database:rows:list", kwargs={"table_id": table.id})
    response = api_client.get(
        f"{url}?user_field_names=true&order_by=field_{field_1.id}",
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_ORDER_BY_FIELD_NOT_FOUND"
    assert (
        response_json["detail"]
        == f"The field field_{field_1.id} was not found in the table."
    )
