import pytest
from django.test import override_settings
from baserow.contrib.database.webhooks.exceptions import (
    TableWebhookAlreadyExists,
    TableWebhookDoesNotExist,
    TableWebhookMaxAllowedCountExceeded,
)

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
    webhook_data["events"] = ["row.Created"]

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
    assert events[0].event_type == "row.Created"

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
        "url": "https://avaliddomain.de/endpoint",
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
        webhook_handler.get(webhook.id)
