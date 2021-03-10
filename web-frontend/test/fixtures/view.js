export function mockTableNameForId(tableId) {
  return `mock_table_${tableId}`
}

export function createMockGridView(
  mock,
  { databaseId = 1, tableId = 1, viewType = 'grid', viewId = 1, filters = [] }
) {
  mock.onGet(`/database/views/table/${tableId}/`).reply(200, [
    {
      id: viewId,
      table_id: tableId,
      name: `mock_view_${viewId}`,
      order: 0,
      type: viewType,
      table: {
        id: tableId,
        name: mockTableNameForId(tableId),
        order: 0,
        database_id: databaseId,
      },
      filter_type: 'AND',
      filters_disabled: false,
      filters,
    },
  ])
}
