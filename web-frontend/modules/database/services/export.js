export default (client) => {
  return {
    export(tableId, viewId, exporterType, values) {
      return client.post(`/database/export/table/${tableId}/`, {
        exporter_type: exporterType.type,
        view_id: viewId,
        ...values,
      })
    },
    get(jobId) {
      return client.get(`/database/export/${jobId}/`)
    },
  }
}
