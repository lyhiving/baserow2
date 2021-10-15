from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from baserow.contrib.database.api.tokens.authentications import TokenAuthentication
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
        webhooks = webhook_handler.get_webhooks_per_table(
            table=table, user=request.user
        )
        return Response(TableWebhookResultSerializer(webhooks, many=True).data)

    @transaction.atomic
    @map_exceptions(
        {
            NoPermissionToTable: ERROR_NO_PERMISSION_TO_TABLE,
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
            table=table, user=request.user, **data
        )
        return Response(TableWebhookResultSerializer(webhook).data)


class TableWebhookView(APIView):
    def get(self, request, table_id, webhook_id):
        raise NotImplementedError
