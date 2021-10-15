from django.db import transaction
from django.conf import settings
from django.db.models.query import QuerySet
from requests import request, ConnectionError
from django.db.models import Q, F
from typing import List, Union

from .models import (
    TableWebhook,
    TableWebhookCall,
    TableWebhookEvents,
    TableWebhookHeader,
)
from .exceptions import (
    TableWebhookAlreadyExists,
    TableWebhookDoesNotExist,
    TableWebhookMaxAllowedCountExceeded,
    TableWebhookCannotBeCalled,
)
from baserow.contrib.database.table.models import GeneratedTableModel


class WebhookHandler:
    def grab_related_webhooks(
        self, table_id: int, event_type: str
    ) -> List[TableWebhook]:

        filter = Q(
            table_id=table_id, active=True, events__event_type__in=[event_type]
        ) | Q(table_id=table_id, active=True, include_all_events=True)
        list_of_hooks = TableWebhook.objects.filter(filter)
        return list_of_hooks

    def get(self, id) -> TableWebhook:
        try:
            webhook = TableWebhook.objects.get(id=id)
        except TableWebhook.DoesNotExist:
            raise TableWebhookDoesNotExist(f"The webhook with id {id} does not exist.")
        return webhook

    def get_webhooks_per_table(self, table: GeneratedTableModel, user: any) -> QuerySet:
        group = table.database.group
        group.has_user(user, raise_error=True)
        return TableWebhook.objects.filter(table_id=table.id)

    def _get_default_headers(self):
        return [{"header": "Content-type", "value": "application/json"}]

    def create_table_webhook(
        self, table: GeneratedTableModel, user: any, data: any
    ) -> TableWebhook:

        group = table.database.group
        group.has_user(user, raise_error=True)

        webhook_already_exists = TableWebhook.objects.filter(
            url=data["url"], table_id=table.id
        ).exists()

        if webhook_already_exists:
            raise TableWebhookAlreadyExists

        webhook_count = TableWebhook.objects.filter(table_id=table.id).count()

        if webhook_count == settings.WEBHOOKS_MAX_PER_TABLE:
            raise TableWebhookMaxAllowedCountExceeded

        events = data.pop("events")
        headers = data.pop("headers")
        data["table_id"] = table.id

        webhook = TableWebhook.objects.create(**data)

        if events is not None and not data["include_all_events"]:
            TableWebhookEvents.objects.bulk_create(
                [TableWebhookEvents(event_type=x, webhook_id=webhook) for x in events]
            )

        # default header
        default_headers = self._get_default_headers()

        # additional user provided headers
        if headers is not None:
            headers = [*default_headers, *headers]
        else:
            headers = default_headers

        TableWebhookHeader.objects.bulk_create(
            [
                TableWebhookHeader(
                    header=x["header"], value=x["value"], webhook_id=webhook
                )
                for x in headers
            ]
        )
        return webhook

    def update_table_webhook(
        self, webhook_id: int, table: GeneratedTableModel, user: any, data: any
    ) -> TableWebhook:

        group = table.database.group
        group.has_user(user, raise_error=True)

        with transaction.atomic():
            try:
                webhook = TableWebhook.objects.select_for_update().get(id=webhook_id)
            except TableWebhook.DoesNotExist:
                raise TableWebhookDoesNotExist(
                    f"The webhook with id {webhook_id} does not exist."
                )
            webhook.name = data["name"]
            webhook.save()
        return webhook

    def delete_table_webhook(
        self, webhook_id: int, table: GeneratedTableModel, user: any
    ) -> None:

        group = table.database.group
        group.has_user(user, raise_error=True)

        TableWebhook.objects.filter(id=webhook_id).delete()

    def call(self, id, payload, event_id, event_type):
        headers = self.create_headers(id, event_id, event_type)
        webhook = TableWebhook.objects.get(id=id)
        try:
            response = request(
                webhook.request_method,
                webhook.url,
                headers=headers,
                json=payload,
                timeout=5,
            )
        except ConnectionError:
            TableWebhookCall.objects.update_or_create(
                event_id=event_id,
                webhook_id=webhook,
                defaults=dict(
                    status_code=500,
                    request=payload,
                    called_url=webhook.url,
                    response="",
                ),
            )
            raise TableWebhookCannotBeCalled

        if not response.status_code == 200 and not response.status_code == 201:
            TableWebhookCall.objects.update_or_create(
                event_id=event_id,
                webhook_id=webhook,
                defaults=dict(
                    status_code=response.status_code,
                    request=payload,
                    called_url=webhook.url,
                    response=response.text,
                ),
            )
            raise TableWebhookCannotBeCalled

        TableWebhookCall.objects.update_or_create(
            event_id=event_id,
            webhook_id=webhook,
            defaults=dict(
                status_code=response.status_code,
                request=payload,
                called_url=webhook.url,
                response=response.text,
            ),
        )

        self.reset_failed_trigger(webhook)

        return True

    def create_headers(self, id, event_id, event_type) -> dict:
        headers = TableWebhookHeader.objects.filter(webhook_id=id)
        headers_dict = {}
        for header in headers:
            headers_dict[header.header] = header.value

        headers_dict["X-Baserow-Event"] = event_type
        headers_dict["X-Baserow-Delivery"] = event_id
        return headers_dict

    def reset_failed_trigger(self, webhook: Union[TableWebhook, int]) -> None:
        if not isinstance(webhook, TableWebhook):
            webhook = self.get(webhook)

        webhook.failed_triggers = 0
        webhook.save()

    def increment_failed_trigger(self, id):
        return TableWebhook.objects.filter(id=id).update(
            failed_triggers=F("failed_triggers") + 1
        )

    def deactivate_webhook(self, id):
        return TableWebhook.objects.filter(id=id).update(active=False)

    def get_trigger_count(self, id) -> int:
        result = TableWebhook.objects.get(id=id)
        return result.failed_triggers
