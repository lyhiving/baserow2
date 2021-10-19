import pytest

from unittest.mock import patch

from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db(transaction=True)
@patch("baserow.contrib.database.webhooks.registries.call_webhook")
def test_row_created(mock_call_webhook, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    data_fixture.create_table_webhook(
        user=user,
        table=table,
        url="http://mydomain.de/endpoint",
        include_all_events=False,
        events=["row.created"],
    )
    field = data_fixture.create_text_field(table=table)
    mock_call_webhook.delay.assert_not_called()
    row_1 = RowHandler().create_row(
        user=user, table=table, values={f"field_{field.id}": "Test"}
    )
    mock_call_webhook.delay.assert_called_once()
    RowHandler().update_row(
        user=user, table=table, row_id=row_1.id, values={f"field_{field.id}": "Test 2"}
    )
    RowHandler().delete_row(user=user, table=table, row_id=row_1.id)

    mock_call_webhook.delay.assert_called_once()

    # make sure that webhook is still only called once after
    # a row has been created in a different table
    table_2 = data_fixture.create_database_table(user=user)
    field_2 = data_fixture.create_text_field(table=table_2)
    RowHandler().create_row(
        user=user, table=table_2, values={f"field_{field_2.id}": "Test"}
    )
    mock_call_webhook.delay.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch("baserow.contrib.database.webhooks.registries.call_webhook")
def test_row_updated(mock_call_webhook, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    data_fixture.create_table_webhook(
        user=user,
        table=table,
        url="http://mydomain.de/endpoint",
        include_all_events=False,
        events=["row.updated"],
    )
    field = data_fixture.create_text_field(table=table)
    mock_call_webhook.delay.assert_not_called()
    row_1 = RowHandler().create_row(
        user=user, table=table, values={f"field_{field.id}": "Test"}
    )
    mock_call_webhook.delay.assert_not_called()
    RowHandler().update_row(
        user=user, table=table, row_id=row_1.id, values={f"field_{field.id}": "Test 2"}
    )
    mock_call_webhook.delay.assert_called_once()
    RowHandler().delete_row(user=user, table=table, row_id=row_1.id)
    mock_call_webhook.delay.assert_called_once()

    # make sure that webhook is still only called once after
    # a row has been updated in a different table
    table_2 = data_fixture.create_database_table(user=user)
    field_2 = data_fixture.create_text_field(table=table_2)
    row = RowHandler().create_row(
        user=user, table=table_2, values={f"field_{field_2.id}": "Test"}
    )
    RowHandler().update_row(
        user=user, table=table_2, row_id=row.id, values={f"field_{field_2.id}": "Test"}
    )
    RowHandler().delete_row(user=user, table=table_2, row_id=row.id)
    mock_call_webhook.delay.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch("baserow.contrib.database.webhooks.registries.call_webhook")
def test_row_deleted(mock_call_webhook, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    data_fixture.create_table_webhook(
        user=user,
        table=table,
        url="http://mydomain.de/endpoint",
        include_all_events=False,
        events=["row.deleted"],
    )
    field = data_fixture.create_text_field(table=table)
    mock_call_webhook.delay.assert_not_called()
    row_1 = RowHandler().create_row(
        user=user, table=table, values={f"field_{field.id}": "Test"}
    )
    RowHandler().update_row(
        user=user, table=table, row_id=row_1.id, values={f"field_{field.id}": "Test 2"}
    )
    mock_call_webhook.delay.assert_not_called()
    RowHandler().delete_row(user=user, table=table, row_id=row_1.id)
    mock_call_webhook.delay.assert_called_once()

    # make sure that webhook is still only called once after
    # a row has been deleted in a different table
    table_2 = data_fixture.create_database_table(user=user)
    field_2 = data_fixture.create_text_field(table=table_2)
    row = RowHandler().create_row(
        user=user, table=table_2, values={f"field_{field_2.id}": "Test"}
    )
    RowHandler().update_row(
        user=user, table=table_2, row_id=row.id, values={f"field_{field.id}": "Test 2"}
    )
    RowHandler().delete_row(user=user, table=table_2, row_id=row.id)
    mock_call_webhook.delay.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch("baserow.contrib.database.webhooks.registries.call_webhook")
def test_row_all_events(mock_call_webhook, data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)
    data_fixture.create_table_webhook(
        user=user,
        table=table,
        url="http://mydomain.de/endpoint",
        include_all_events=True,
    )
    field = data_fixture.create_text_field(table=table)
    mock_call_webhook.delay.assert_not_called()
    row_1 = RowHandler().create_row(
        user=user, table=table, values={f"field_{field.id}": "Test"}
    )
    RowHandler().update_row(
        user=user, table=table, row_id=row_1.id, values={f"field_{field.id}": "Test 2"}
    )
    RowHandler().delete_row(user=user, table=table, row_id=row_1.id)
    assert mock_call_webhook.delay.call_count == 3

    # make sure that webhook is still only called three times after a row has been
    # created, updated, deleted in a different table
    table_2 = data_fixture.create_database_table(user=user)
    field_2 = data_fixture.create_text_field(table=table_2)
    row = RowHandler().create_row(
        user=user, table=table_2, values={f"field_{field_2.id}": "Test"}
    )
    RowHandler().update_row(
        user=user, table=table_2, row_id=row.id, values={f"field_{field.id}": "Test 2"}
    )
    RowHandler().delete_row(user=user, table=table_2, row_id=row.id)
    assert mock_call_webhook.delay.call_count == 3
