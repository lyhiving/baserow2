export default (client) => {
  return {
    export(tableId, viewId, exporterType, exporterOptions) {
      const exporterOptionsJson = exporterType.convertOptionsToJson(
        exporterOptions
      )
      const tableOrView = viewId !== null ? 'view' : 'table'
      const id = viewId !== null ? viewId : tableId
      return client.post(`/database/export/${tableOrView}/${id}/`, {
        exporter_type: exporterType.type,
        ...exporterOptionsJson,
      })
    },
    get(jobId) {
      return client.get(`/database/export/${jobId}/`)
    },
  }
}
