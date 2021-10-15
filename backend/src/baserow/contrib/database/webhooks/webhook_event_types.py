from .registries import WebhookEventType
from baserow.contrib.database.rows.signals import row_created

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
