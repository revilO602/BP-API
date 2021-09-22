from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import connection
from django.http import JsonResponse
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.generics import GenericAPIView, CreateAPIView

from account.api.serializers import AccountSerializer

from account.models import Account


# Respond with json of uptime
@api_view(['GET', ])
def uptime(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        row = cursor.fetchone()
    uptime = str(row[0])
    uptime = uptime.replace(',', '')
    return JsonResponse({"psql": {"uptime": uptime}})


class AccountRegistrationView(GenericAPIView, CreateModelMixin):
    """
    View to register a new user account.

    * Return info of the created account.
    """
    serializer_class = AccountSerializer

    def post(self, request):
        return self.create(request)


class AccountView(GenericAPIView, RetrieveModelMixin, DestroyModelMixin):
    """
    View to update, retrieve or delete the account of the authenticated user.
    * Requires authentication by a JWT token.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request):
        instance = self.get_object()
        serializer = AccountSerializer(instance=instance, data=request.data, partial=True)
        res_status = status.HTTP_400_BAD_REQUEST
        serializer.is_valid(raise_exception=True)
        serializer.save(instance=request.user, validated_data=serializer.validated_data)
        res_status = status.HTTP_201_CREATED
        return Response(serializer.data, status=res_status)

    def get(self, request):
        return self.retrieve(self, request)

