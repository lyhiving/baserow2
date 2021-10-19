from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.api.tokens.authentications import TokenAuthentication
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.webhooks.exceptions import TableWebhookDoesNotExist
from .serializers import TableWebhookRequestSerializer, TableWebhookResultSerializer
from baserow.contrib.database.tokens.handler import TokenHandler
from baserow.contrib.database.webhooks.handler import WebhookHandler
from baserow.contrib.database.table.handler import TableHandler
from baserow.contrib.database.tokens.exceptions import NoPermissionToTable
from baserow.contrib.database.api.tokens.errors import ERROR_NO_PERMISSION_TO_TABLE

from baserow.api.decorators import map_exceptions, validate_body


class TableWebhooksView(APIView):
    authentication_classes = APIView.authentication_classes + [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

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

    @transaction.atomic
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
        }
    )
    @validate_body(TableWebhookRequestSerializer)
    def post(self, request, data, table_id):
        """
        Creates a new webhook for a given table.
        """

        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        TokenHandler().check_table_permissions(request, "create", table, False)
        webhook = webhook_handler.create_table_webhook(
            table=table, user=request.user, data=data
        )
        return Response(TableWebhookResultSerializer(webhook).data)


class TableWebhookView(APIView):
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
            TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
            TableWebhookDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
        }
    )
    def get(self, request, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        TokenHandler().check_table_permissions(request, "create", table, False)
        webhook = webhook_handler.get_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user
        )
        return Response(TableWebhookResultSerializer(webhook).data)

    @validate_body(TableWebhookRequestSerializer)
    def patch(self, request, data, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        TokenHandler().check_table_permissions(request, "create", table, False)
        webhook = webhook_handler.update_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user, data=data
        )
        return Response(TableWebhookResultSerializer(webhook).data)

    def delete(self, request, table_id, webhook_id):
        table = TableHandler().get_table(table_id)
        webhook_handler = WebhookHandler()
        TokenHandler().check_table_permissions(request, "create", table, False)
        webhook_handler.delete_table_webhook(
            webhook_id=webhook_id, table=table, user=request.user
        )
        return Response(data="OK", status=200)
