export default (client) => {
  return {
    export(tableId, viewId, exporterType, exporterOptions) {
      let exporterOptionsJson = {}
      if (exporterType === 'csv') {
        exporterOptionsJson = {
          csv_include_header: exporterOptions.csvFirstRowHeader,
          csv_charset: exporterOptions.csvEncoding,
          csv_column_separator: exporterOptions.csvColumnSeparator,
        }
      } else {
        throw new Error(
          `Unsupported type ${exporterType} given to export service.`
        )
      }

      const tableOrView = viewId !== null ? 'view' : 'table'
      const id = viewId !== null ? viewId : tableId
      return client.post(`/database/export/${tableOrView}/${id}/`, {
        exporter_type: exporterType,
        ...exporterOptionsJson,
      })
    },
    get(jobId) {
      return client.get(`/database/export/${jobId}/`)
    },
  }
}
