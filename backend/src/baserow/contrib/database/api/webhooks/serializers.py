from rest_framework import serializers

from baserow.contrib.database.api.webhooks.validators import (
    url_validation,
    http_header_validation,
    validate_events_data,
)

from baserow.contrib.database.webhooks.models import (
    TableWebhook,
    TableWebhookCall,
    TableWebhookEvents,
    TableWebhookHeader,
)
from baserow.contrib.database.webhooks.registries import webhook_event_type_registry


class TableWebhookEventsSerializer(serializers.ListField):
    child = serializers.ChoiceField(choices=webhook_event_type_registry.get_types())


class TableWebhookHeaderSerializer(serializers.Serializer):
    header = serializers.CharField(min_length=2)
    value = serializers.CharField(min_length=2)


class TableWebhookCreateRequestSerializer(serializers.ModelSerializer):
    events = TableWebhookEventsSerializer(required=False)
    url = serializers.URLField(validators=[url_validation])
    headers = serializers.ListField(
        required=False,
        child=TableWebhookHeaderSerializer(),
        validators=[http_header_validation],
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
        return validate_events_data(data)


class TableWebhookUpdateRequestSerializer(serializers.ModelSerializer):
    events = TableWebhookEventsSerializer(required=False)
    headers = serializers.ListField(
        required=False,
        child=TableWebhookHeaderSerializer(),
        validators=[http_header_validation],
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
            "active",
        )
        extra_kwargs = {
            "url": {"required": False},
            "name": {"required": False},
            "active": {"required": False},
            "request_method": {"required": False},
        }

    def validate(self, data):
        return validate_events_data(data)


class TableWebhookEventsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableWebhookEvents
        fields = ["event_type"]


class TableWebhookHeaderResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableWebhookHeader
        fields = "__all__"


class TableWebhookResultSerializer(serializers.ModelSerializer):
    events = TableWebhookEventsResponseSerializer(many=True)
    headers = TableWebhookHeaderResponseSerializer(many=True)

    class Meta:
        model = TableWebhook
        fields = "__all__"


class TableWebhookCallResponse(serializers.ModelSerializer):
    class Meta:
        model = TableWebhookCall
        fields = "__all__"
