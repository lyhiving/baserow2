from baserow.contrib.database.webhooks.models import TableWebhook, TableWebhookEvents


class TableWebhookFixture:
    def create_table_webhook(self, user=None, **kwargs):
        if "table" not in kwargs:
            kwargs["table"] = self.create_database_table(user=user)

        kwargs["table_id"] = kwargs["table"].id
        kwargs.pop("table")

        if "url" not in kwargs:
            kwargs["url"] = self.fake.url()

        if "include_all_events" not in kwargs:
            kwargs["include_all_events"] = True

        if "events" in kwargs:
            events = kwargs.pop("events")
        else:
            events = []

        webhook = TableWebhook.objects.create(**kwargs)

        if not len(events) == 0 and not kwargs["include_all_events"]:
            TableWebhookEvents.objects.bulk_create(
                [TableWebhookEvents(event_type=x, webhook_id=webhook) for x in events]
            )

        return webhook
