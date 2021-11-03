from .registries import WebhookEventType
from baserow.contrib.database.rows.signals import row_created, row_updated, row_deleted


class RowCreatedEventType(WebhookEventType):

    type = "row.created"
    signal = row_created


class RowUpdatedEventType(WebhookEventType):

    type = "row.updated"
    signal = row_updated


class RowDeletedEventType(WebhookEventType):

    type = "row.deleted"
    signal = row_deleted

    def get_payload(self, **kwargs):
        table = kwargs.get("table")
        row = kwargs.get("row")
        payload = {"table_id": table.id, "row_id": row.id, "values": {}}
        return payload
