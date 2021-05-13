EXPORT_JOB_ERRORS = [("EXAMPLE_ERROR", "EXAMPLE_ERROR")]


class ExportAlreadyRunningException(Exception):
    pass


class ExportJobCanceledException(Exception):
    pass
