from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.permissions import IsRegistering
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.generics import GenericAPIView

from accounts.api.serializers import AccountSerializer


class AccountsView(GenericAPIView, CreateModelMixin):
    """
    View to create a new account or retrieve a list of accounts.
    * Requires authentication by a JWT token.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated | IsRegistering]

    def post(self, request):
        return self.create(request)


class AccountDetailView(APIView, DestroyModelMixin):
    """
    View to update, retrieve or delete a single account.
    * Requires authentication by a JWT token.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated | IsRegistering]

    def get_object(self, account_id):
        if account_id == 'me':
            return self.request.user

    def patch(self, request, account_id):
        instance = self.get_object(account_id)
        serializer = AccountSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response(serializer.data)

    def get(self, request, account_id):
        instance = self.get_object(account_id)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

