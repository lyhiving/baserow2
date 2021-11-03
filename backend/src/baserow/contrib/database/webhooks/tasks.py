from django.conf import settings
from baserow.config.celery import app
from .exceptions import TableWebhookCannotBeCalled


@app.task(bind=True, max_retries=settings.WEBHHOKS_MAX_RETRIES_PER_CALL)
def call_webhook(self, **kwargs):
    from .handler import WebhookHandler

    webhook_handler = WebhookHandler()
    webhook_id = kwargs.get("webhook_id")
    payload = kwargs.get("payload")
    event_id = kwargs.get("event_id")
    event_type = kwargs.get("event_type")
    try:
        webhook_handler.call(webhook_id, payload, event_id, event_type)
    except TableWebhookCannotBeCalled as exc:
        if self.request.retries < settings.WEBHHOKS_MAX_RETRIES_PER_CALL:
            self.retry(exc=exc, countdown=2 ** self.request.retries)
        else:
            if (
                webhook_handler.get_trigger_count(webhook_id)
                < settings.WEBHOOKS_MAX_CONSECUTIVE_TRIGGER_FAILURES
            ):
                webhook_handler.increment_failed_trigger(webhook_id)
                return
            else:
                webhook_handler.deactivate_webhook(webhook_id)
                return

    webhook_handler.reset_failed_trigger(webhook_id)
