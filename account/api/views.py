from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.generics import GenericAPIView

from account.api.serializers import AccountSerializer
from couriers.models import Courier


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
        serializer.is_valid(raise_exception=True)
        serializer.save(instance=request.user, validated_data=serializer.validated_data)
        res_status = status.HTTP_201_CREATED
        return Response(serializer.data, status=res_status)

    def get(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if Courier.objects.filter(user=instance).exists():
            newdict = {'is_courier': True}
        else: newdict = {'is_courier': False}
        newdict.update(serializer.data)
        return Response(newdict)

