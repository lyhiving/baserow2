class ExportJobCanceledException(Exception):
    pass


class TableOnlyExportUnsupported(Exception):
    pass


class ViewUnsupportedForExporterType(Exception):
    pass
