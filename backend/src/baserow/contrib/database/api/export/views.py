from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import (
    ERROR_USER_NOT_IN_GROUP,
    ERROR_USER_INVALID_GROUP_PERMISSIONS,
)
from baserow.contrib.database.api.export.errors import (
    ExportJobDoesNotExistException,
    ERROR_EXPORT_JOB_DOES_NOT_EXIST,
)
from baserow.contrib.database.api.export.serializers import (
    CreateExportJobSerializer,
    GetExportJobSerializer,
)
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.api.views.errors import ERROR_VIEW_DOES_NOT_EXIST
from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.export.models import ExportJob
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.views.exceptions import ViewDoesNotExist
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.export.tasks import run_export_job
from baserow.core.exceptions import UserNotInGroup, UserInvalidGroupPermissionsError


class ExportTableView(APIView):
    permission_classes = (IsAuthenticated,)

    @validate_body(CreateExportJobSerializer)
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            UserInvalidGroupPermissionsError: ERROR_USER_INVALID_GROUP_PERMISSIONS,
        }
    )
    def post(self, request, table_id, data):
        table = TableHandler().get_table(table_id)
        table.database.group.has_user(request.user, raise_error=True)

        return _export(
            request.user, table, None, data["exporter_type"], data["exporter_options"]
        )


def _export(user, table, view, exporter_type, export_options):
    job = ExportHandler().create_pending_export_job(
        user, table, view, exporter_type, export_options
    )
    run_export_job.delay(job.id)
    return Response(GetExportJobSerializer(job).data)


class ExportViewView(APIView):
    permission_classes = (IsAuthenticated,)

    @validate_body(CreateExportJobSerializer)
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            UserInvalidGroupPermissionsError: ERROR_USER_INVALID_GROUP_PERMISSIONS,
        }
    )
    def post(self, request, view_id, data):
        view = ViewHandler().get_view(view_id)
        view.table.database.group.has_user(request.user, raise_error=True)

        return _export(
            request.user,
            view.table,
            view,
            data["exporter_type"],
            data["exporter_options"],
        )


class ExportJobView(APIView):
    permission_classes = (IsAuthenticated,)

    @map_exceptions(
        {
            ExportJobDoesNotExistException: ERROR_EXPORT_JOB_DOES_NOT_EXIST,
        }
    )
    def get(self, request, job_id):
        try:
            job = ExportJob.objects.get(id=job_id)
        except ExportJob.DoesNotExist:
            raise ExportJobDoesNotExistException()

        if job.user != request.user:
            raise ExportJobDoesNotExistException()

        return Response(GetExportJobSerializer(job).data)
