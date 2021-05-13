export default (client) => {
  return {
    export(tableId, viewId, exporterType, exporterOptions) {
      const exporterOptionsJson = {
        csv_include_header: exporterOptions.csvFirstRowHeader,
        csv_encoding: exporterOptions.csvEncoding,
        csv_column_separator: exporterOptions.csvColumnSeparator,
      }
      const tableOrView = viewId !== null ? 'view' : 'table'
      const id = viewId !== null ? viewId : tableId
      return client.post(`/database/export/${tableOrView}/${id}/`, {
        exporter_type: exporterType,
        exporter_options: exporterOptionsJson,
      })
    },
    get(jobId) {
      return client.get(`/database/export/${jobId}/`)
    },
  }
}
