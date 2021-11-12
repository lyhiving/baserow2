import pytest
import responses
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

    # make sure that 'active' is ignored when creating a new webhook
    webhook_create_data["url"] = "https://mydomain.com/endpoint2"
    webhook_create_data["include_all_events"] = True
    webhook_create_data["events"] = []
    webhook_create_data["active"] = False

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == HTTP_200_OK
    assert response_json["active"] is True

    # make sure it's not possible to create empty headers
    webhook_create_data["url"] = "https://mydomain.com/endpoint3"
    webhook_create_data["headers"] = [{"header": "", "value": ""}]

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST

    # make sure it's not possible to create same headers twice
    webhook_create_data["headers"] = [
        {"header": "Content-length", "value": "20"},
        {"header": "Content-length", "value": "50"},
    ]

    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response_json["error"] == "ERROR_REQUEST_BODY_VALIDATION"
    assert response_json["detail"]["headers"][0]["code"] == "ambigous_headers"


@pytest.mark.django_db
def test_update_webhooks(api_client, data_fixture):
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
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    webhook_id = response_json["id"]
    assert response.status_code == HTTP_200_OK

    webhook_update_data = {
        "name": "My new name",
    }

    response = api_client.patch(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        dict(webhook_update_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK

    webhook_update_data = {
        "request_method": "GET",
    }

    response = api_client.patch(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        dict(webhook_update_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK

    # make sure that 'include_all_events' cannot be set to False without providing
    # events that this webhook will be subscribed to
    webhook_update_data = {"include_all_events": False}

    response = api_client.patch(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        dict(webhook_update_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST

    webhook_update_data["events"] = ["row.created"]

    response = api_client.patch(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        dict(webhook_update_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_delete_webhooks(api_client, data_fixture):
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
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    webhook_id = response_json["id"]
    assert response.status_code == HTTP_200_OK

    response = api_client.delete(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    assert response.status_code == HTTP_200_OK

    # trying to delete same webhook twice will simply return 'OK'
    response = api_client.delete(
        reverse(
            "api:database:tables:webhook",
            kwargs={"table_id": table.id, "webhook_id": webhook_id},
        ),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
@responses.activate
def test_call_webhooks(api_client, data_fixture):
    user, jwt_token = data_fixture.create_user_and_token(
        email="test@test.nl", password="password", first_name="Test1"
    )
    table = data_fixture.create_database_table(user=user)

    webhook_create_data = {
        "url": "https://mydomain.com/endpoint",
        "request_method": "POST",
        "name": "My Webhook",
        "include_all_events": True,
    }
    webhook_call_body = {"event_type": "row.created", "webhook": webhook_create_data}
    response = api_client.post(
        reverse("api:database:tables:list_webhooks", kwargs={"table_id": table.id}),
        dict(webhook_create_data),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )
    response_json = response.json()
    assert response.status_code == HTTP_200_OK

    # mocked responses
    mocked_response = {"is_response": True}
    responses.add(
        responses.POST, webhook_create_data["url"], json=mocked_response, status=400
    )
    responses.add(
        responses.POST, webhook_create_data["url"], json=mocked_response, status=200
    )

    response = api_client.post(
        reverse(
            "api:database:tables:call_webhook",
            kwargs={"table_id": table.id},
        ),
        dict(webhook_call_body),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status_code"] == 400

    response = api_client.post(
        reverse(
            "api:database:tables:call_webhook",
            kwargs={"table_id": table.id},
        ),
        dict(webhook_call_body),
        format="json",
        HTTP_AUTHORIZATION=f"JWT {jwt_token}",
    )

    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status_code"] == 200
