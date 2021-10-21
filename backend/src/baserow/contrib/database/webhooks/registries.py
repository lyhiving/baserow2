import uuid
from django.dispatch.dispatcher import Signal
from baserow.contrib.database.webhooks.handler import WebhookHandler

from baserow.core.registry import (
    ModelRegistryMixin,
    Registry,
    Instance,
)

from .tasks import call_webhook


class WebhookEventType(Instance):
    """
    @TODO docstring
    """

    def __init__(self):
        if not isinstance(self.signal, Signal):
            raise Exception

        self.connect_to_signal()
        super().__init__()

    def connect_to_signal(self):
        self.signal.connect(self.listener)

    def listener(self, **kwargs):
        payload = self.get_payload(**kwargs)
        table_id = kwargs.get("table").id
        webhook_handler = WebhookHandler()
        webhooks = webhook_handler.find_webhooks_to_call(table_id, self.type)
        event_id = uuid.uuid4()
        for webhook in webhooks:
            call_webhook.delay(
                webhook_id=webhook.id,
                payload=payload,
                event_id=event_id,
                event_type=self.type,
            )


class WebhookEventTypeRegistry(ModelRegistryMixin, Registry):
    name = "webhook_event"


webhook_event_type_registry = WebhookEventTypeRegistry()
