import uuid
import json
from typing import List

from django.db import transaction
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models import Q

from baserow.contrib.database.api.rows.serializers import (
    get_row_serializer_class,
    RowSerializer,
)
from baserow.contrib.database.table.models import Table
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


class WebhookHandler:
    def get_example_payload(
        self,
        use_user_field_names: bool,
        table: Table,
        event_type="row.created",
    ):
        """
        Generates an example payload off the related table, to be used when manually
        calling a webhook endpoint.
        """

        model = table.get_model()
        serializer = get_row_serializer_class(
            model,
            RowSerializer,
            is_response=True,
            user_field_names=use_user_field_names,
        )
        instance = model(id=1, order=1)
        serialized_data = serializer(instance).data
        types_mapping = {
            "row.created": {"values": serialized_data},
            "row.updated": {"values": serialized_data, "old_values": serialized_data},
            "row.deleted": {},
        }
        event_specific_payload = types_mapping[event_type]

        payload_base = {
            "table_id": table.id,
            "row_id": 1,
            "event_type": event_type,
        }

        payload = {**payload_base, **event_specific_payload}

        return payload

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
        self, webhook_id: int, table: Table, user: any
    ) -> TableWebhook:
        """
        Verifies that the calling user has access to the specified table and if so
        returns the webhook
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        return self._get_table_webhook(webhook_id)

    def _get_table_webhook(self, webhook_id: int) -> TableWebhook:
        """
        Gets a single webhook for the provided webhookd ID. Raises a
        'TableWebhookDoesNotExist' exception if no webhook for the given ID can be
        found.
        """

        try:
            webhook = TableWebhook.objects.get(id=webhook_id)
        except TableWebhook.DoesNotExist:
            raise TableWebhookDoesNotExist(
                f"The webhook with id {webhook_id} does not exist."
            )

        return webhook

    def get_all_table_webhooks(self, table: Table, user: any) -> QuerySet:
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

    def create_table_webhook(self, table: Table, user: any, data: any) -> TableWebhook:
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
        self, webhook_id: int, table: Table, user: any, data: any
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

            if "include_all_events" in data and data["include_all_events"]:
                TableWebhookEvents.objects.filter(webhook_id=webhook_id).delete()

            # additional user provided headers
            if headers is not None:
                for header in headers:
                    TableWebhookHeader.objects.get_or_create(
                        header=header["header"],
                        value=header["value"],
                        webhook_id=webhook,
                    )
            webhook.save()
        return webhook

    def delete_table_webhook(self, webhook_id: int, table: Table, user: any) -> None:
        """
        Deletes a specific table webhook.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        TableWebhook.objects.filter(id=webhook_id).delete()

    def call_from_task(
        self, webhook_id: int, payload: dict, event_id: str, event_type: str
    ):
        """
        Calls a specific webhook and stores the result in the database. This function
        is to be used from a celery task. After each call it will also call a call log
        cleanup function.
        """

        headers = self.create_headers(webhook_id, event_id, event_type)
        webhook: TableWebhook = self._get_table_webhook(webhook_id)
        webhook_call_defaults = dict(
            request="",
            called_url=webhook.url,
            response="",
            error="",
        )
        response = self.make_request(
            webhook.request_method, webhook.url, headers, payload
        )
        webhook_call_defaults["request"] = response["request"]
        webhook_call_defaults["status_code"] = response["status_code"]

        if response["is_unreachable"]:
            webhook_call_defaults["error"] = response["exception"]
            self._create_or_update_webhook_call(
                webhook, event_id, event_type, webhook_call_defaults
            )
            raise TableWebhookCannotBeCalled

        webhook_call_defaults["status_code"] = response["status_code"]
        webhook_call_defaults["response"] = response["response"]
        self._create_or_update_webhook_call(
            webhook, event_id, event_type, webhook_call_defaults
        )

        self._delete_webhook_calls(webhook)
        if response["status_code"] != 200 and response["status_code"] != 201:
            # we raise the exception here so that the task calling this method
            # will know to retry the webhook call.
            raise TableWebhookCannotBeCalled

        return True

    def test_call(self, table: Table, user: any, **kwargs):
        """
        Helps with running a manual test call triggered by the user. It will generate
        an event_id, as well as uses a "manual.call" event type to indicate that this
        was a user generated call.
        """

        group = table.database.group
        group.has_user(user, raise_error=True)

        event_id = str(uuid.uuid4())
        event_type = kwargs.get("event_type", "row.created")
        webhook_data = kwargs.get("webhook")
        use_user_field_names = webhook_data.get("use_user_field_names")
        request_method = webhook_data.get("request_method")
        additional_headers = webhook_data.get("headers")
        url = webhook_data.get("url")
        example_payload = self.get_example_payload(
            use_user_field_names, table, event_type=event_type
        )
        default_headers = self._get_default_headers()
        baserow_headers = self.baserow_headers(event_type, event_id)
        all_headers = [*default_headers, *baserow_headers]

        if additional_headers is not None:
            all_headers = [*all_headers, *additional_headers]

        assembled_headers = self.assemble_headers(all_headers)

        response = self.make_request(
            request_method, url, assembled_headers, example_payload
        )

        return response

    def make_request(self, method: str, url: str, headers: dict, payload: str) -> dict:
        if settings.DEBUG is True:
            from requests import Request, Session, RequestException
        else:
            from advocate import (
                Request,
                Session,
                RequestException,
                UnacceptableAddressException,
            )

        request = Request(method, url, headers=headers, json=payload)
        prepped = request.prepare()
        request_text = self.formatted_request(prepped)
        try:
            s = Session()
            response = s.send(prepped, timeout=5)
            formatted_response = self.formatted_response(response)
            return {
                "response": formatted_response,
                "request": request_text,
                "status_code": response.status_code,
                "is_unreachable": False,
                "exception": "",
            }
        except RequestException as e:
            return {
                "response": "",
                "request": request_text,
                "status_code": None,
                "is_unreachable": True,
                "exception": repr(e),
            }
        except UnacceptableAddressException as e:
            return {
                "response": "",
                "request": "",
                "status_code": None,
                "is_unreachable": True,
                "exception": repr(e),
            }

    def formatted_request(self, req):
        """
        Helper function, which will format a requests request object.
        """
        return "{}\r\n{}\r\n\r\n{}".format(
            req.method + " " + req.url,
            "\r\n".join("{}: {}".format(k, v) for k, v in req.headers.items()),
            json.dumps(json.loads(req.body), indent=4),
        )

    def formatted_response(self, resp):
        """
        Helper function, which will format a requests response. It will try to format
        the response body as json and if it is not a valid json it will fallback to
        text.
        """

        try:
            response_body = resp.json()
            response_body = json.dumps(response_body, indent=4)
        except Exception:
            response_body = resp.text

        return "{}\r\n\r\n{}".format(
            "\r\n".join("{}: {}".format(k, v) for k, v in resp.headers.items()),
            response_body,
        )

    def get_call_events_per_webhook(self, webhook_id: int):
        """
        Returns every call log entry for a given webhook.
        Orders by called_time, returns the last call first.
        """

        return TableWebhookCall.objects.filter(webhook_id=webhook_id).order_by(
            "-called_time"
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
        headers = TableWebhookHeader.objects.filter(webhook_id=webhook_id).values()
        baserow_headers = self.baserow_headers(event_type, event_id)
        all_headers = [*headers, *baserow_headers]
        return self.assemble_headers(all_headers)

    def baserow_headers(self, event_type: str, event_id: str):
        e_type = {"header": "X-Baserow-Event", "value": event_type}
        id = {"header": "X-Baserow-Delivery", "value": event_id}
        return [e_type, id]

    def assemble_headers(self, headers: List[dict]):
        """
        Helper function, which will turn a list of header objects into a requests
        expected dictionary where the header is the key and the value is the value.
        """

        headers_dict = {}
        for header in headers:
            headers_dict[header["header"]] = header["value"]
        return headers_dict

    def reset_failed_trigger(self, webhook_id: int) -> None:
        webhook = self._get_table_webhook(webhook_id)
        webhook.failed_triggers = 0
        webhook.save()

    def increment_failed_trigger(self, webhook_id: int) -> None:
        webhook = self._get_table_webhook(webhook_id)
        webhook.failed_triggers += 1
        webhook.save()

    def deactivate_webhook(self, webhook_id: int) -> None:
        webhook = self._get_table_webhook(webhook_id)
        webhook.active = False
        webhook.save()

    def get_trigger_count(self, webhook_id: int) -> int:
        webhook = self._get_table_webhook(webhook_id)
        return webhook.failed_triggers
