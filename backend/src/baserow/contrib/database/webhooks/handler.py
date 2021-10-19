import json
from django.db import transaction
from django.conf import settings
from django.db.models.query import QuerySet
from requests import request, ConnectionError
from django.db.models import Q, F

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
    def find_webhooks_to_call(self, table_id: int, event_type: str) -> QuerySet:
        """
        This function is responsible for finding all the webhooks related to a table
        for which a webhooks event occured. It will return a queryset with the filtered
        webhooks based on whether the webhook is active and if the webhooks 'includes
        all events' or just the specific event that occured.
        """

        specific_event_filter = Q(
            table_id=table_id, active=True, events__event_type__in=[event_type]
        )
        all_events_filter = Q(table_id=table_id, active=True, include_all_events=True)
        filter = specific_event_filter | all_events_filter
        return TableWebhook.objects.filter(filter)

    def get_table_webhook(
        self, webhook_id: int, table: GeneratedTableModel, user: any
    ) -> TableWebhook:
        """
        Gets a single webhook for the provided webhookd ID. Raises a
        'TableWebhookDoesNotExist' exception if no webhook for the given ID can be
        found.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        try:
            webhook = TableWebhook.objects.get(id=webhook_id)
        except TableWebhook.DoesNotExist:
            raise TableWebhookDoesNotExist(
                f"The webhook with id {webhook_id} does not exist."
            )

        return webhook

    def get_all_table_webhooks(self, table: GeneratedTableModel, user: any) -> QuerySet:
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

        events = data.pop("events", None)
        headers = data.pop("headers", None)
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

            events = data.pop("events")
            headers = data.pop("headers")

            for name, value in data.items():
                setattr(webhook, name, value)

            if events is not None and not data["include_all_events"]:
                for event in events:
                    TableWebhookEvents.objects.get_or_create(
                        event_type=event,
                        webhook_id=webhook,
                    )

            # default header
            default_headers = self._get_default_headers()

            # additional user provided headers
            if headers is not None:
                headers = [*default_headers, *headers]
            else:
                headers = default_headers

            for header in headers:
                TableWebhookHeader.objects.get_or_create(
                    header=header["header"],
                    value=header["value"],
                    webhook_id=webhook,
                )
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
        webhook_call_defaults = dict(
            status_code=500,
            request=json.dumps(payload),
            called_url=webhook.url,
            response="",
        )
        try:
            response = request(
                webhook.request_method,
                webhook.url,
                headers=headers,
                json=payload,
                timeout=5,
            )
        except ConnectionError:
            self._create_or_update_webhook_call(
                webhook, event_id, webhook_call_defaults
            )
            raise TableWebhookCannotBeCalled

        if not response.status_code == 200 and not response.status_code == 201:
            webhook_call_defaults["status_code"] = response.status_code
            webhook_call_defaults["response"] = response.text
            self._create_or_update_webhook_call(
                webhook, event_id, webhook_call_defaults
            )
            raise TableWebhookCannotBeCalled

        webhook_call_defaults["status_code"] = response.status_code
        webhook_call_defaults["response"] = response.text
        self._create_or_update_webhook_call(webhook, event_id, webhook_call_defaults)

        return True

    def _create_or_update_webhook_call(
        self, webhook: TableWebhook, event_id: str, defaults: dict
    ):
        return TableWebhookCall.objects.update_or_create(
            event_id=event_id, webhook_id=webhook, defaults=defaults
        )

    def create_headers(self, id, event_id, event_type) -> dict:
        headers = TableWebhookHeader.objects.filter(webhook_id=id)
        headers_dict = {}
        for header in headers:
            headers_dict[header.header] = header.value

        headers_dict["X-Baserow-Event"] = event_type
        headers_dict["X-Baserow-Delivery"] = event_id
        return headers_dict

    def reset_failed_trigger(self, webhook_id: int) -> None:
        return TableWebhook.objects.filter(id=webhook_id).update(failed_triggers=0)

    def increment_failed_trigger(self, id):
        return TableWebhook.objects.filter(id=id).update(
            failed_triggers=F("failed_triggers") + 1
        )

    def deactivate_webhook(self, id):
        return TableWebhook.objects.filter(id=id).update(active=False)

    def get_trigger_count(self, webhook_id) -> int:
        try:
            webhook = TableWebhook.objects.get(id=webhook_id)
        except TableWebhook.DoesNotExist:
            raise TableWebhookDoesNotExist(
                f"The webhook with id {webhook_id} does not exist."
            )
        return webhook.failed_triggers
