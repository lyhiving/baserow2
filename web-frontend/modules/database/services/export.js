export default (client) => {
  return {
    export(tableId, viewId, exporterType, exporterOptions) {
      const exporterOptionsJson = exporterType.convertOptionsToJson(
        exporterOptions
      )
      return client.post(`/database/export/table/${tableId}/`, {
        exporter_type: exporterType.type,
        view_id: viewId,
        ...exporterOptionsJson,
      })
    },
    get(jobId) {
      return client.get(`/database/export/${jobId}/`)
    },
  }
}
