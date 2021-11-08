from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from drf_spectacular.utils import extend_schema
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.schemas import get_error_schema
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.api.tokens.authentications import TokenAuthentication
from baserow.contrib.database.api.webhooks.errors import (
    ERROR_TABLE_WEBHOOK_ALREADY_EXISTS,
    ERROR_TABLE_WEBHOOK_MAX_LIMIT_EXCEEDED,
    ERROR_TABLE_WEBHOOK_DOES_NOT_EXIST,
    ERROR_TABLE_WEBHOOK_CANNOT_BE_CALLED,
)
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.webhooks.exceptions import (
    TableWebhookAlreadyExists,
    TableWebhookDoesNotExist,
    TableWebhookMaxAllowedCountExceeded,
    TableWebhookCannotBeCalled,
)
from baserow.core.exceptions import UserNotInGroup
from .serializers import (
    TableWebhookCreateRequestSerializer,
    TableWebhookResultSerializer,
    TableWebhookUpdateRequestSerializer,
)
from baserow.contrib.database.webhooks.handler import WebhookHandler
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.tokens.exceptions import NoPermissionToTable
from baserow.contrib.database.api.tokens.errors import ERROR_NO_PERMISSION_TO_TABLE

from baserow.api.decorators import map_exceptions, validate_body


class TableWebhooksView(APIView):
    authentication_classes = APIView.authentication_classes + [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table for which to retrieve the webhooks.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="list_database_table_webhooks",
        description="Lists all the webhooks for the given table.",
        responses={
            200: TableWebhookResultSerializer(many=True),
            400: get_error_schema(["ERROR_USER_NOT_IN_GROUP"]),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions(
        {
            UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
        }
    )
    def get(self, request, table_id):
        """
        Lists all the webhooks of a given table.
        """

        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        webhooks = webhook_handler.get_all_table_webhooks(
            table=table, user=request.user
        )
        return Response(TableWebhookResultSerializer(webhooks, many=True).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table for which the webhook shall be "
                "created.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="create_database_table_webhook",
        description="Create a webhook for a given table.",
        request=TableWebhookCreateRequestSerializer(),
        responses={
            200: TableWebhookResultSerializer(),
            400: get_error_schema(
                ["ERROR_USER_NOT_IN_GROUP", "ERROR_TABLE_WEBHOOK_MAX_LIMIT_EXCEEDED"]
            ),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @transaction.atomic
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            TableWebhookMaxAllowedCountExceeded: ERROR_TABLE_WEBHOOK_MAX_LIMIT_EXCEEDED,
            TableWebhookAlreadyExists: ERROR_TABLE_WEBHOOK_ALREADY_EXISTS,
        }
    )
    @validate_body(TableWebhookCreateRequestSerializer)
    def post(self, request, data, table_id):
        """
        Creates a new webhook for a given table.
        """

        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        webhook = webhook_handler.create_table_webhook(
            table=table, user=request.user, data=data
        )
        return Response(TableWebhookResultSerializer(webhook).data)


class TableWebhookView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table for which to retrieve the webhook.",
            ),
            OpenApiParameter(
                name="webhook_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the webhook that shall be retrieved.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="get_database_table_webhook",
        description="Returns an existing, single webhook.",
        responses={
            200: TableWebhookResultSerializer(),
            400: get_error_schema(["ERROR_USER_NOT_IN_GROUP"]),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(
                ["ERROR_TABLE_DOES_NOT_EXIST", "ERROR_TABLE_WEBHOOK_DOES_NOT_EXIST"]
            ),
        },
    )
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            TableWebhookDoesNotExist: ERROR_TABLE_WEBHOOK_DOES_NOT_EXIST,
        }
    )
    def get(self, request, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        webhook = webhook_handler.get_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user
        )
        return Response(TableWebhookResultSerializer(webhook).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table under which the webhook was created.",
            ),
            OpenApiParameter(
                name="webhook_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the webhook that shall be updated.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="update_database_table_webhook",
        description="Update a specific table webhook.",
        request=TableWebhookCreateRequestSerializer(),
        responses={
            200: TableWebhookResultSerializer(),
            400: get_error_schema(["ERROR_USER_NOT_IN_GROUP"]),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(
                ["ERROR_TABLE_DOES_NOT_EXIST", "ERROR_TABLE_WEBHOOK_DOES_NOT_EXIST"]
            ),
        },
    )
    @validate_body(TableWebhookUpdateRequestSerializer)
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            TableWebhookDoesNotExist: ERROR_TABLE_WEBHOOK_DOES_NOT_EXIST,
        }
    )
    def patch(self, request, data, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        webhook = webhook_handler.update_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user, data=data
        )
        return Response(TableWebhookResultSerializer(webhook).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table under which the webhook was created.",
            ),
            OpenApiParameter(
                name="webhook_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the webhook that shall be deleted.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="delete_database_table_webhook",
        description="Delete a specific table webhook.",
        request=TableWebhookCreateRequestSerializer(),
        responses={
            400: get_error_schema(["ERROR_USER_NOT_IN_GROUP"]),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
        }
    )
    def delete(self, request, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        webhook_handler.delete_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user
        )
        return Response(data="OK", status=200)


class TableWebhookCallView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="table_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the table under which the webhook was created.",
            ),
            OpenApiParameter(
                name="webhook_id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="The ID of the webhook that shall be called.",
            ),
        ],
        tags=["Database table webhooks"],
        operation_id="call_database_table_webhook",
        description="Manually calls a specific table webhook.",
        request=TableWebhookCreateRequestSerializer(),
        responses={
            400: get_error_schema(
                ["ERROR_USER_NOT_IN_GROUP", "ERROR_TABLE_WEBHOOK_CANNOT_BE_CALLED"]
            ),
            401: get_error_schema(["ERROR_NO_PERMISSION_TO_TABLE"]),
            404: get_error_schema(["ERROR_TABLE_DOES_NOT_EXIST"]),
        },
    )
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            TableWebhookCannotBeCalled: ERROR_TABLE_WEBHOOK_CANNOT_BE_CALLED,
        }
    )
    @validate_body(TableWebhookCreateRequestSerializer)
    def post(self, request, data, table_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        data = webhook_handler.test_call(table, request.user, **data)
        data_response = {
            "request": data["request"],
            "response": data["response"],
            "status_code": data["status"],
        }
        return Response(data=data_response, status=200)
