from rest_framework import serializers

from baserow.contrib.database.api.webhooks.validators import (
    url_validation,
    http_header_validation,
)

from baserow.contrib.database.webhooks.models import (
    TableWebhook,
    TableWebhookEvents,
)
from baserow.contrib.database.webhooks.registries import webhook_event_type_registry


class TableWebhookEventsSerializer(serializers.ListField):
    child = serializers.ChoiceField(choices=webhook_event_type_registry.get_types())


class TableWebhookHeaderSerializer(serializers.ListField):
    header = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class TableWebhookRequestSerializer(serializers.ModelSerializer):
    events = TableWebhookEventsSerializer(required=False)
    url = serializers.URLField(validators=[url_validation])
    headers = TableWebhookHeaderSerializer(
        required=False, validators=[http_header_validation]
    )

    class Meta:
        model = TableWebhook
        fields = (
            "url",
            "include_all_events",
            "events",
            "request_method",
            "headers",
            "name",
        )

    def validate(self, data):
        data_dict = dict(data)
        data_keys = data.keys()
        include_all_events: bool = data_dict.get("include_all_events")
        if not include_all_events and "events" not in data_keys:
            raise serializers.ValidationError("events must be provided")
        return data


class TableWebhookEventsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableWebhookEvents
        fields = ["event_type"]


class TableWebhookResultSerializer(serializers.ModelSerializer):
    events = TableWebhookEventsResponseSerializer(many=True)

    class Meta:
        model = TableWebhook
        fields = "__all__"
