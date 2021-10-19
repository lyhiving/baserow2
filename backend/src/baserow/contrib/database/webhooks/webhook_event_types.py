from .registries import WebhookEventType
from baserow.contrib.database.rows.signals import row_created, row_updated, row_deleted

from baserow.contrib.database.api.rows.serializers import (
    RowSerializer,
    get_row_serializer_class,
)


class RowCreatedEventType(WebhookEventType):

    type = "row.created"
    signal = row_created

    def get_payload(self, **kwargs):
        model = kwargs.get("model")
        row = kwargs.get("row")
        serialized_row = get_row_serializer_class(
            model, RowSerializer, is_response=True
        )(row).data

        return serialized_row


class RowUpdatedEventType(WebhookEventType):

    type = "row.updated"
    signal = row_updated

    def get_payload(self, **kwargs):
        model = kwargs.get("model")
        row = kwargs.get("row")
        serialized_row = get_row_serializer_class(
            model, RowSerializer, is_response=True
        )(row).data

        return serialized_row


class RowDeletedEventType(WebhookEventType):

    type = "row.deleted"
    signal = row_deleted

    def get_payload(self, **kwargs):
        model = kwargs.get("model")
        row = kwargs.get("row")
        serialized_row = get_row_serializer_class(
            model, RowSerializer, is_response=True
        )(row).data

        return serialized_row
