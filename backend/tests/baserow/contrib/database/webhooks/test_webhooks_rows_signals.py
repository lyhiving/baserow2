import pytest

from unittest.mock import patch

from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db(transaction=True)
@patch("baserow.contrib.database.webhooks.registries.call_webhook")
def test_row_created(mock_call_webhook, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    webhook = data_fixture.create_table_webhook(
        user=user, table=table, url="http://mydomain.de/endpoint"
    )
    field = data_fixture.create_text_field(table=table)
    assert webhook
    mock_call_webhook.delay.assert_not_called()
    RowHandler().create_row(
        user=user, table=table, values={f"field_{field.id}": "Test"}
    )

    mock_call_webhook.delay.assert_called_once()

    # make sure that webhook is still only called once after
    # a row has been created in a different table
    table_2 = data_fixture.create_database_table(user=user)
    field_2 = data_fixture.create_text_field(table=table_2)
    RowHandler().create_row(
        user=user, table=table_2, values={f"field_{field_2.id}": "Test"}
    )
    mock_call_webhook.delay.assert_called_once()
