from typing import Dict, Any, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.functional import lazy
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from baserow.api.decorators import map_exceptions
from baserow.api.errors import (
    ERROR_USER_NOT_IN_GROUP,
    ERROR_USER_INVALID_GROUP_PERMISSIONS,
)
from baserow.api.schemas import get_error_schema
from baserow.api.utils import validate_data, PolymorphicMappingSerializer
from baserow.contrib.database.api.export.errors import (
    ExportJobDoesNotExistException,
    ERROR_EXPORT_JOB_DOES_NOT_EXIST,
    ERROR_VIEW_UNSUPPORTED_FOR_EXPORT_TYPE,
    ERROR_TABLE_ONLY_EXPORT_UNSUPPORTED,
)
from baserow.contrib.database.api.export.serializers import (
    ExportJobSerializer,
    BaseExporterOptionsSerializer,
)
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.api.views.errors import ERROR_VIEW_DOES_NOT_EXIST
from baserow.contrib.database.export.exceptions import (
    ViewUnsupportedForExporterType,
    TableOnlyExportUnsupported,
)
from baserow.contrib.database.export.handler import ExportHandler
from baserow.contrib.database.export.models import ExportJob
from baserow.contrib.database.export.registries import table_exporter_registry
from baserow.contrib.database.export.tasks import run_export_job
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.table.models import Table
from baserow.contrib.database.views.exceptions import ViewDoesNotExist
from baserow.contrib.database.views.handler import ViewHandler
from baserow.contrib.database.views.models import View
from baserow.core.exceptions import UserNotInGroup, UserInvalidGroupPermissionsError

User = get_user_model()

# A placeholder serializer only used to generate correct api documentation.
CreateExportJobSerializer = PolymorphicMappingSerializer(
    "Export",
    lazy(table_exporter_registry.get_option_serializer_map, dict)(),
    type_field_name="exporter_type",
)


def _validate_options(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Looks up the exporter_type from the data, selects the correct export
    options serializer based on the exporter_type and finally validates the data using
    that serializer.

    :param data: A dict of data to serialize using an exporter options serializer.
    :return: validated export options data
    """
    option_serializers = table_exporter_registry.get_option_serializer_map()
    validated_exporter_type = validate_data(BaseExporterOptionsSerializer, data)
    serializer = option_serializers[validated_exporter_type["exporter_type"]]
    return validate_data(serializer, data)


def _create_and_start_new_job(
    user: User, table: Table, view: Optional[View], export_options: Dict[str, Any]
) -> Response:
    job = ExportHandler.create_pending_export_job(user, table, view, export_options)
    # Ensure we only trigger the job after the transaction we are in has committed
    # and created the export job in the database. Otherwise the job might run before
    # we commit and crash as there is no job yet.
    transaction.on_commit(lambda: run_export_job.delay(job.id))
    return Response(ExportJobSerializer(job).data)


class ExportTableView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The table id to create and start an export job for",
            )
        ],
        tags=["Export"],
        operation_id="export_table",
        description=(
            "Creates and starts a new export job for a table given some exporter "
            "options. Returns an error if the requesting user does not have permissions"
            "to view the table."
        ),
        request=CreateExportJobSerializer,
        responses={
            200: ExportJobSerializer,
            400: get_error_schema(
                [
                    "ERROR_USER_NOT_IN_GROUP",
                    "ERROR_REQUEST_BODY_VALIDATION",
                    "ERROR_USER_INVALID_GROUP_PERMISSIONS",
                    "ERROR_TABLE_ONLY_EXPORT_UNSUPPORTED",
                ]
            ),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            UserInvalidGroupPermissionsError: ERROR_USER_INVALID_GROUP_PERMISSIONS,
            TableOnlyExportUnsupported: ERROR_TABLE_ONLY_EXPORT_UNSUPPORTED,
        }
    )
    def post(self, request, table_id):
        """
        Starts a new export job for the provided table, export type and options.
        """
        table = TableHandler().get_table(table_id)
        table.database.group.has_user(request.user, raise_error=True)

        option_data = _validate_options(request.data)

        return _create_and_start_new_job(request.user, table, None, option_data)


class ExportViewView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="view_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The view id to create and start an export job for.",
            )
        ],
        tags=["Export"],
        operation_id="export_view",
        description=(
            "Creates and starts a new export job for a view given some exporter "
            "options. Returns an error if the requesting user does not have permissions"
            "to view the view."
        ),
        request=CreateExportJobSerializer,
        responses={
            200: ExportJobSerializer,
            400: get_error_schema(
                [
                    "ERROR_USER_NOT_IN_GROUP",
                    "ERROR_REQUEST_BODY_VALIDATION",
                    "ERROR_USER_INVALID_GROUP_PERMISSIONS",
                    "ERROR_VIEW_UNSUPPORTED_FOR_EXPORT_TYPE",
                ]
            ),
            404: get_error_schema(["ERROR_VIEW_DOES_NOT_EXIST"]),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            ViewDoesNotExist: ERROR_VIEW_DOES_NOT_EXIST,
            UserInvalidGroupPermissionsError: ERROR_USER_INVALID_GROUP_PERMISSIONS,
            ViewUnsupportedForExporterType: ERROR_VIEW_UNSUPPORTED_FOR_EXPORT_TYPE,
        }
    )
    def post(self, request, view_id):
        """
        Starts a new export job for the provided view, export type and options.
        """
        view = ViewHandler().get_view(view_id)

        option_data = _validate_options(request.data)

        return _create_and_start_new_job(
            request.user,
            view.table,
            view,
            option_data,
        )


class ExportJobView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="job_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The job id to lookup information about.",
            )
        ],
        tags=["Export"],
        operation_id="get_export_job",
        description=(
            "Returns information such as export progress and status or the url of the "
            "exported file for the specified export job, only if the requesting user "
            "has access."
        ),
        responses={
            200: ExportJobSerializer,
            400: get_error_schema(
                [
                    "ERROR_REQUEST_BODY_VALIDATION",
                ]
            ),
            404: get_error_schema(["ERROR_EXPORT_JOB_DOES_NOT_EXIST"]),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            ExportJobDoesNotExistException: ERROR_EXPORT_JOB_DOES_NOT_EXIST,
        }
    )
    def get(self, request, job_id):
        """
        Retrieves the specified export job.
        """
        try:
            job = ExportJob.objects.get(id=job_id)
        except ExportJob.DoesNotExist:
            raise ExportJobDoesNotExistException()

        if job.user != request.user:
            raise ExportJobDoesNotExistException()

        return Response(ExportJobSerializer(job).data)
