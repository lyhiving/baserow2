from django.db import models

from baserow.core.models import CreatedAndUpdatedOnMixin


class TableWebhook(CreatedAndUpdatedOnMixin, models.Model):
    table_id = models.IntegerField()
    active = models.BooleanField(default=True)
    url = models.URLField()

    class RequestMethod(models.TextChoices):
        POST = "POST"
        GET = "GET"
        PUT = "PUT"
        PATCH = "PATCH"
        DELETE = "DELETE"

    request_method = models.CharField(
        max_length=10,
        choices=RequestMethod.choices,
        default=RequestMethod.POST,
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    include_all_events = models.BooleanField(default=True)
    failed_triggers = models.IntegerField(default=0)

    class Meta:
        unique_together = ("table_id", "url", "request_method")


class TableWebhookEvents(CreatedAndUpdatedOnMixin, models.Model):
    event_type = models.CharField(max_length=50)
    webhook_id = models.ForeignKey(
        TableWebhook, related_name="events", on_delete=models.CASCADE
    )


class TableWebhookHeader(models.Model):
    webhook_id = models.ForeignKey(
        TableWebhook, related_name="headers", on_delete=models.CASCADE
    )
    header = models.TextField()
    value = models.TextField()


class TableWebhookCall(models.Model):
    event_id = models.UUIDField()
    event_type = models.CharField(max_length=50)
    webhook_id = models.ForeignKey(
        TableWebhook, related_name="calls", on_delete=models.CASCADE
    )
    called_time = models.DateTimeField(auto_now_add=True)
    called_url = models.URLField()
    status_code = models.IntegerField()
    request = models.TextField(null=True)
    response = models.TextField(null=True)
