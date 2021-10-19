import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from django.shortcuts import reverse


@pytest.mark.django_db
def test_create_webhooks(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)

    webhook_create_data = {
        "url": "https://mydomain.com/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
    }
    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": 99999}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json()["error"] == "ERROR_TABLE_DOES_NOT_EXIST"

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        webhook_create_data,
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    assert response.status_code == HTTP_200_OK

    webhook_create_data["include_all_events"] = False

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"

    webhook_create_data["events"] = ["row.row"]

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response_json["detail"]["events"]["0"][0]["code"] == "invalid_choice"
