export function createMockRowsInGridView(mock, { gridId = 1, rows = 1 }) {
  mock.onGet(`/database/views/grid/${gridId}/`).reply(200, {
    count: rows.length,
    results: rows,
  })
}
