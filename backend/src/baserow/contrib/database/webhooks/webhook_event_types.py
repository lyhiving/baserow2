from baserow.contrib.database.api.rows.serializers import (
    get_row_serializer_class,
    RowSerializer,
)
from baserow.contrib.database.rows.signals import row_created, row_updated, row_deleted
from .registries import WebhookEventType


class RowCreatedEventType(WebhookEventType):

    type = "row.created"
    signal = row_created


class RowUpdatedEventType(WebhookEventType):

    type = "row.updated"
    signal = row_updated

    def get_payload(self, **kwargs):
        model = kwargs.get("model")
        table = kwargs.get("table")
        row = kwargs.get("row")
        user_field_names = kwargs.get("user_field_names", True)
        row_before_update = kwargs.get("before_return")
        serialized_row_new = get_row_serializer_class(
            model, RowSerializer, is_response=True, user_field_names=user_field_names
        )(row).data
        serialized_row_old = get_row_serializer_class(
            model, RowSerializer, is_response=True, user_field_names=user_field_names
        )(row_before_update).data
        payload = {
            "table_id": table.id,
            "row_id": row.id,
            "event_type": self.type,
            "values": serialized_row_new,
            "old_values": serialized_row_old,
        }

        return payload


class RowDeletedEventType(WebhookEventType):

    type = "row.deleted"
    signal = row_deleted

    def get_payload(self, **kwargs):
        table = kwargs.get("table")
        row = kwargs.get("row")
        payload = {
            "table_id": table.id,
            "row_id": row.id,
            "event_type": self.type,
            "values": {},
        }
        return payload
