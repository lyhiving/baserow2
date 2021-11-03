import json
import uuid
import pytest
import responses

from django.test import override_settings
from baserow.contrib.database.webhooks.exceptions import (
    TableWebhookAlreadyExists,
    TableWebhookCannotBeCalled,
    TableWebhookDoesNotExist,
    TableWebhookMaxAllowedCountExceeded,
)
from baserow.contrib.database.webhooks.models import TableWebhookCall

from baserow.core.exceptions import UserNotInGroup
from baserow.contrib.database.webhooks.handler import WebhookHandler


@pytest.mark.django_db(transaction=True)
@override_settings(WEBHOOKS_MAX_PER_TABLE=3)
def test_create_webhook(data_fixture):
    user = data_fixture.create_user()
    user_2 = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }
    with pytest.raises(UserNotInGroup):
        webhook_handler.create_table_webhook(
            table=table, user=user_2, data=dict(webhook_data)
        )

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    assert webhook.name == webhook_data["name"]
    assert webhook.url == webhook_data["url"]
    assert webhook.include_all_events == webhook_data["include_all_events"]
    assert webhook.table_id == table.id
    assert webhook.request_method == "POST"
    events = webhook.events.all()
    assert len(events) == 0
    headers = webhook.headers.all()
    assert len(headers) == 1
    assert headers[0].header == "Content-type"
    assert headers[0].value == "application/json"

    # if we try to create another webhook for the same table with the same url
    # we expect an exception to be raised.
    with pytest.raises(TableWebhookAlreadyExists):
        webhook_handler.create_table_webhook(
            table=table, user=user, data=dict(webhook_data)
        )

    # new url
    webhook_data["url"] = "https://seconddomain.de/endpoint"

    # if "include_all_events" is True and we pass in events that are not empty
    # the handler will not create the entry in the events table.
    webhook_data["events"] = ["row.created"]

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    events = webhook.events.all()
    assert len(events) == 0

    # when we set "include_all_events" to False then we expect that the events will be
    # added

    webhook_data["include_all_events"] = False
    webhook_data["url"] = "https://thirddomain.de/endpoint"
    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    events = webhook.events.all()
    assert len(events) == 1
    assert events[0].event_type == "row.created"

    # check that we can't create more than "MAX_ALLOWED_WEBHOOKS" per table
    webhook_data["include_all_events"] = True
    webhook_data["url"] = "https://fourthdomain.de/endpoint"

    with pytest.raises(TableWebhookMaxAllowedCountExceeded):
        webhook_handler.create_table_webhook(
            table=table, user=user, data=dict(webhook_data)
        )


@pytest.mark.django_db(transaction=True)
def test_update_webhook(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    webhook_update_data = {
        "webhook_id": webhook.id,
        "url": "https://avaliddomain.de/updated_endpoint",
        "name": "My Webhook New Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )

    assert updated_webhook.name == webhook_update_data["name"]
    assert updated_webhook.url == webhook_update_data["url"]

    webhook_update_data["events"] = ["row.created"]

    # since "include_all_events" is still true we expect no events to be added
    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )
    assert len(updated_webhook.events.all()) == 0

    webhook_update_data["include_all_events"] = False
    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )
    events = updated_webhook.events.all()
    assert len(events) == 1
    assert events[0].event_type == "row.created"

    # after activating "include_all_events" again, we expect the added events to be
    # removed
    webhook_update_data["include_all_events"] = True
    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )
    events = updated_webhook.events.all()
    assert len(events) == 0

    webhook_update_data["headers"] = [{"header": "Authorization", "value": "12345"}]
    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )
    headers = updated_webhook.headers.all()
    assert len(headers) == 2
    assert headers[0].header == "Content-type"
    assert headers[0].value == "application/json"
    assert headers[1].header == "Authorization"
    assert headers[1].value == "12345"

    # it should be possible to deactivate a webhook
    webhook_update_data["active"] = False
    updated_webhook = webhook_handler.update_table_webhook(
        webhook_id=webhook.id, table=table, user=user, data=dict(webhook_update_data)
    )
    assert updated_webhook.active is False


@pytest.mark.django_db(transaction=True)
def test_get_webhook(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    gotten_webhook = webhook_handler.get_table_webhook(webhook.id, table, user)

    assert gotten_webhook.id == webhook.id

    # trying to get unknown webhook will result in exception
    with pytest.raises(TableWebhookDoesNotExist):
        webhook_handler.get_table_webhook(5000, table, user)

    user_2 = data_fixture.create_user()

    # user with no permission to the table will not be able to access webhook
    with pytest.raises(UserNotInGroup):
        webhook_handler.get_table_webhook(webhook.id, table, user_2)


@pytest.mark.django_db(transaction=True)
def test_get_all_tablewebhooks(data_fixture):
    user = data_fixture.create_user()
    user_2 = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data_1 = {
        "url": "https://avaliddomain.de/first_endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook_data_2 = {
        "url": "https://avaliddomain.de/second_endpoint",
        "name": "My Webhook 2",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook_data_3 = {
        "url": "https://avaliddomain.de/third_endpoint",
        "name": "My Webhook 2",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook_1 = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data_1)
    )
    webhook_2 = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data_2)
    )
    webhook_3 = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data_3)
    )

    with pytest.raises(UserNotInGroup):
        webhook_handler.get_all_table_webhooks(table, user_2)

    webhooks = webhook_handler.get_all_table_webhooks(table, user)

    assert len(webhooks) == 3
    gotten_webhook_ids = [webhook.id for webhook in webhooks].sort()
    webhook_ids = [webhook_1.id, webhook_2.id, webhook_3.id].sort()

    assert gotten_webhook_ids == webhook_ids

    # trying to get table webhooks for a table without any will return empty list

    new_table = data_fixture.create_database_table(user=user)
    webhooks = webhook_handler.get_all_table_webhooks(new_table, user)

    assert len(webhooks) == 0


@pytest.mark.django_db()
def test_delete_webhook(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    webhook_handler.delete_table_webhook(table=table, user=user, webhook_id=webhook.id)

    # trying to get the deleted webhook should now fail
    with pytest.raises(TableWebhookDoesNotExist):
        webhook_handler.get_table_webhook(webhook.id, table, user)


@pytest.mark.django_db()
def test_table_webhook_failed_triggers(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )

    # trigger count will initially be 0

    webhook_failed_triggers_count = webhook_handler.get_trigger_count(webhook.id)
    assert webhook_failed_triggers_count == 0

    # incrementing

    webhook_handler.increment_failed_trigger(webhook.id)
    webhook_failed_triggers_count = webhook_handler.get_trigger_count(webhook.id)
    assert webhook_failed_triggers_count == 1

    # resetting will set the count to 0 again

    webhook_handler.reset_failed_trigger(webhook.id)
    webhook_failed_triggers_count = webhook_handler.get_trigger_count(webhook.id)
    assert webhook_failed_triggers_count == 0

    # getting a trigger count for a webhook that does not exists will raise
    # exception
    with pytest.raises(TableWebhookDoesNotExist):
        webhook_handler.get_trigger_count(5000)


@pytest.mark.django_db()
@responses.activate
def test_calling_webhook(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook_handler = WebhookHandler()

    webhook_data = {
        "url": "https://avaliddomain.de/endpoint",
        "name": "My Webhook",
        "include_all_events": True,
        "request_method": "POST",
        "events": [],
        "headers": [],
    }

    request_payload = {"some": "payload"}
    response = {"some": "response"}

    webhook = webhook_handler.create_table_webhook(
        table=table, user=user, data=dict(webhook_data)
    )
    # mocked responses
    responses.add(responses.POST, webhook_data["url"], json=response, status=400)
    responses.add(responses.POST, webhook_data["url"], json=response, status=200)

    event_id = uuid.uuid4()

    with pytest.raises(TableWebhookCannotBeCalled):
        webhook_handler.call(webhook.id, request_payload, str(event_id), "row_created")

    call = TableWebhookCall.objects.filter(webhook_id=webhook, event_id=event_id)

    assert len(call) == 1
    assert call[0].called_url == webhook_data["url"]
    assert call[0].status_code == 400
    assert call[0].request == json.dumps(request_payload)
    assert call[0].response == json.dumps(response)

    # calling a second time with success will update the initial call db entry

    webhook_handler.call(webhook.id, request_payload, str(event_id), "row_created")

    call = TableWebhookCall.objects.filter(webhook_id=webhook, event_id=event_id)

    assert len(call) == 1
    assert call[0].called_url == webhook_data["url"]
    assert call[0].status_code == 200
    assert call[0].request == json.dumps(request_payload)
    assert call[0].response == json.dumps(response)
