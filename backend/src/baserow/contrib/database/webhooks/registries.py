import uuid

from django.dispatch.dispatcher import Signal

from baserow.contrib.database.api.rows.serializers import (
    RowSerializer,
    get_row_serializer_class,
)
from baserow.contrib.database.webhooks.handler import WebhookHandler
from baserow.core.registry import (
    ModelRegistryMixin,
    Registry,
    Instance,
)
from .tasks import call_webhook


class WebhookEventType(Instance):
    """
    This class represents a custom webhook event type that can be added to the webhook
    event type registry.
    Each registered event type needs to set a django signal on which it will listen on.
    Upon initialization the webhook event type will connect to the django signal.

    The 'listener' function will be called for every received signal. The listener will
    generate a unique ID for every received signal, find all webhooks that need to be
    called and subsequently generates the payload for every webhook and runs a celery
    task that will do the actuall call to the endpoint.
    """

    def __init__(self):
        if not isinstance(self.signal, Signal):
            raise Exception

        self.connect_to_signal()
        super().__init__()

    def connect_to_signal(self):
        self.signal.connect(self.listener)

    def get_payload(self, **kwargs):
        model = kwargs.get("model")
        table = kwargs.get("table")
        row = kwargs.get("row")
        user_field_names = kwargs.get("user_field_names", True)
        serialized_row = get_row_serializer_class(
            model, RowSerializer, is_response=True, user_field_names=user_field_names
        )(row).data
        payload = {
            "table_id": table.id,
            "row_id": row.id,
            "event_type": self.type,
            "values": serialized_row,
        }

        return payload

    def listener(self, **kwargs):
        table_id = kwargs.get("table").id
        webhook_handler = WebhookHandler()
        webhooks = webhook_handler.find_webhooks_to_call(table_id, self.type)
        event_id = uuid.uuid4()
        for webhook in webhooks:
            payload = self.get_payload(
                user_field_names=webhook.use_user_field_names, **kwargs
            )
            call_webhook.delay(
                webhook_id=webhook.id,
                payload=payload,
                event_id=event_id,
                event_type=self.type,
            )


class WebhookEventTypeRegistry(ModelRegistryMixin, Registry):
    name = "webhook_event"


webhook_event_type_registry = WebhookEventTypeRegistry()
