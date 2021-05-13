from rest_framework.status import HTTP_404_NOT_FOUND

ERROR_EXPORT_JOB_DOES_NOT_EXIST = (
    "ERROR_EXPORT_JOB_DOES_NOT_EXIST",
    HTTP_404_NOT_FOUND,
    "That export job does not exist",
)


class ExportJobDoesNotExistException(Exception):
    pass
