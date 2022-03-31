from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from accounts.permissions import IsRegistering
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.generics import GenericAPIView

from accounts.api.serializers import AccountSerializer
from bpproject.settings import DEBUG

class AccountsView(GenericAPIView, CreateModelMixin):
    """
    View to create a new account or retrieve a list of accounts.
    * Requires authentication by a JWT token.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated | IsRegistering]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        if not DEBUG:
            token = PasswordResetTokenGenerator().make_token(new_user)
            send_mail('Email verification', f'http://localhost:8000/api/verification/{token}', None, [new_user.email])
        else:
            new_user.is_active = True
            new_user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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

@api_view(['GET', ])
def mail(request):
    send_mail(
        'Subject here',
        'Here is the message.',
        None,
        ['leontiev.oliver@gmail.com'],
    )
