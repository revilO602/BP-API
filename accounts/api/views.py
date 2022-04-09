from django.shortcuts import get_object_or_404, render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Account
from accounts.permissions import IsRegistering
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.generics import GenericAPIView
from accounts.api.serializers import AccountSerializer, TokenObtainSerializerWithActiveCheck
from bpproject.settings import DEBUG
from accounts.api.emails import confirmation_email


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
        if DEBUG:
            confirmation_email(new_user)
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


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainSerializerWithActiveCheck


@api_view(['POST', ])
def resend_confirmation_email(request):
    try:
        email = request.data['email']
        user = get_object_or_404(Account, email=email)
        if user.is_active:
            return Response({"email": "Email is already confirmed"}, status=400)
        confirmation_email(user)
    except KeyError:
        return Response({"email": "Field required"}, status=400)
    return Response(status=204)


@api_view(['GET', ])
def email_verification(request, uid, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = Account.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'successful-verification.html')
    else:
        return render(request, 'invalid_verification.html')

# password reset - poslat len email s novym passwordom
