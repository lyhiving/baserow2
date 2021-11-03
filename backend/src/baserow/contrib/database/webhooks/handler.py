import json
import uuid
from django.db import transaction
from django.conf import settings
from django.db.models.query import QuerySet
from requests import request, RequestException
from advocate import request as advocate_request
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

if settings.DEBUG is True:
    request_module = request
else:
    request_module = advocate_request


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
        """
        Gets all the webhooks for a specific table.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)
        return TableWebhook.objects.filter(table_id=table.id).order_by("-id")

    def _get_default_headers(self):
        """
        Internal helper function, responsible for providing default http headers. For
        now we will always set the content-type to "application/json".
        """

        return [{"header": "Content-type", "value": "application/json"}]

    def create_table_webhook(
        self, table: GeneratedTableModel, user: any, data: any
    ) -> TableWebhook:
        """
        Creates a new webhook for a given table.
        """

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
        """
        Updates a specific table webhook.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        with transaction.atomic():
            try:
                webhook = TableWebhook.objects.select_for_update().get(id=webhook_id)
            except TableWebhook.DoesNotExist:
                raise TableWebhookDoesNotExist(
                    f"The webhook with id {webhook_id} does not exist."
                )

            # if the webhook is not active and a user sets the webhook to active
            # we want to make sure to reset the failed_triggers counter
            is_webhook_active = webhook.active
            if "active" in data:
                is_active_new = data.get("active")
                if not is_webhook_active and is_active_new:
                    webhook.failed_triggers = 0

            events = data.pop("events", None)
            headers = data.pop("headers", None)

            for name, value in data.items():
                setattr(webhook, name, value)

            if events is not None and not data["include_all_events"]:
                for event in events:
                    TableWebhookEvents.objects.get_or_create(
                        event_type=event,
                        webhook_id=webhook,
                    )

            if data["include_all_events"]:
                TableWebhookEvents.objects.filter(webhook_id=webhook_id).delete()

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
        """
        Deletes a specific table webhook.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        TableWebhook.objects.filter(id=webhook_id).delete()

    def call(self, webhook_id: int, payload: dict, event_id: str, event_type: str):
        """
        Calls a specific webhook and stores the result in the database. This function
        is to be used from a celery task. After each call it will also call a call log
        cleanup function.
        """

        headers = self.create_headers(webhook_id, event_id, event_type)
        webhook = TableWebhook.objects.get(id=webhook_id)
        webhook_call_defaults = dict(
            status_code=500,
            request=json.dumps(payload),
            called_url=webhook.url,
            response="",
        )
        try:
            response = request_module(
                webhook.request_method,
                webhook.url,
                headers=headers,
                json=payload,
                timeout=5,
            )
        except RequestException:
            # RequestException catches ConnectionError, HTTPError, Timeout or
            # TooManyRedirects
            self._create_or_update_webhook_call(
                webhook, event_id, event_type, webhook_call_defaults
            )
            raise TableWebhookCannotBeCalled

        webhook_call_defaults["status_code"] = response.status_code
        webhook_call_defaults["response"] = response.text
        self._create_or_update_webhook_call(
            webhook, event_id, event_type, webhook_call_defaults
        )

        self._delete_webhook_calls(webhook)
        if response.status_code != 200 and response.status_code != 201:
            # we raise the exception here so that the task calling this method
            # will know to retry the webhook call.
            raise TableWebhookCannotBeCalled

        return True

    def test_call(self, webhook_id: int, example_payload: dict):
        """
        Helps with running a manual test call triggered by the user. It will generate
        an event_id, as well as uses a "manual.call" event type to indicate that this
        was a user generated call.
        """

        event_id = str(uuid.uuid4())
        event_type = "manual.call"

        try:
            self.call(webhook_id, example_payload, event_id, event_type)
            call = TableWebhookCall.objects.get(event_id=event_id)
            return {"response": call.response, "status": call.status_code}
        except Exception:
            raise TableWebhookCannotBeCalled

    def get_call_events_per_webhook(self, webhook_id: int):
        """
        Returns every call log entry for a given webhook.
        """

        return TableWebhookCall.objects.filter(webhook_id=webhook_id).order_by(
            "called_time"
        )

    def _create_or_update_webhook_call(
        self, webhook: TableWebhook, event_id: str, event_type: str, defaults: dict
    ):
        return TableWebhookCall.objects.update_or_create(
            event_id=event_id,
            event_type=event_type,
            webhook_id=webhook,
            defaults=defaults,
        )

    def _delete_webhook_calls(self, webhook: TableWebhook):
        retain = settings.WEBHOOKS_MAX_CALL_LOG_ENTRIES
        objects_to_keep = TableWebhookCall.objects.filter(
            webhook_id=webhook.id
        ).order_by("-called_time")[:retain]
        return TableWebhookCall.objects.exclude(pk__in=objects_to_keep).delete()

    def create_headers(self, webhook_id: int, event_id: str, event_type: str) -> dict:
        headers = TableWebhookHeader.objects.filter(webhook_id=webhook_id)
        headers_dict = {}
        for header in headers:
            headers_dict[header.header] = header.value

        headers_dict["X-Baserow-Event"] = event_type
        headers_dict["X-Baserow-Delivery"] = event_id
        return headers_dict

    def reset_failed_trigger(self, webhook_id: int) -> None:
        return TableWebhook.objects.filter(id=webhook_id).update(failed_triggers=0)

    def increment_failed_trigger(self, webhook_id: int) -> None:
        return TableWebhook.objects.filter(id=webhook_id).update(
            failed_triggers=F("failed_triggers") + 1
        )

    def deactivate_webhook(self, webhook_id: int) -> None:
        return TableWebhook.objects.filter(id=webhook_id).update(active=False)

    def get_trigger_count(self, webhook_id: int) -> int:
        try:
            webhook = TableWebhook.objects.get(id=webhook_id)
        except TableWebhook.DoesNotExist:
            raise TableWebhookDoesNotExist(
                f"The webhook with id {webhook_id} does not exist."
            )
        return webhook.failed_triggers
