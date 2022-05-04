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
from accounts.api.emails import verification_email


class AccountsView(GenericAPIView, CreateModelMixin):
    """
    View that handles operations on accounts.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated | IsRegistering]

    def post(self, request):
        """
        Register new account.

        :param request: HTTP Request with account data in body.
        :return: HTTP Response - 201 if success, 400 if invalid body
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        if DEBUG:
            verification_email(new_user)
        else:
            new_user.is_active = True
            new_user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AccountDetailView(APIView, DestroyModelMixin):
    """
    View to handle operation on a single account.
    * Requires authentication by a JWT token. Returns a 401 response if user is not authenticated.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, account_id):
        """
        Retrieve account instance from database
        * Presently supports only returning own account of authenticated user - through the 'me' ID.

        :param account_id: ID of account to retrieve, if 'me' than retrieve own account
        :return: Account model instance or None
        """
        if account_id == 'me':
            return self.request.user
        else:
            return None

    def patch(self, request, account_id):
        """
        Update account.

        :param request: HTTP PATCH request with all for updated account in body.
        :param account_id: ID of account to update
        :return: HTTP response - 200 if success (with new account data), 403 if not accessing own account
        """
        instance = self.get_object(account_id)
        if not instance:
            return Response({"detail": "Forbidden"}, status=403)
        serializer = AccountSerializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response(serializer.data)

    def get(self, request, account_id):
        """
        Retrieve account data.

        :param request: HTTP GET request
        :param account_id: ID of account to update
        :return: HTTP response - 200 if success (with account data), 403 if not accessing own account
        """
        instance = self.get_object(account_id)
        if not instance:
            return Response({"detail": "Forbidden"}, status=403)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    View that returns a JWT access and refresh token
    """
    serializer_class = TokenObtainSerializerWithActiveCheck


@api_view(['POST', ])
def resend_confirmation_email(request):
    """
    Functional view that resend the verification email.

    :param request: HTTP POST request containing email to send verification link to.
    :return: HTTP Response - 204 if success, 404 if user not registered, 400 if email already confirmed or invalid
    """
    try:
        email = request.data['email']
        user = get_object_or_404(Account, email=email)
        if user.is_active:
            return Response({"email": "Email is already confirmed"}, status=400)
        verification_email(user)
    except KeyError:
        return Response({"email": "Field required"}, status=400)
    return Response(status=204)


@api_view(['GET', ])
def email_verification(request, uid, token):
    """
    Functional view that activates a users account after clicking on the link send in a verification email.

    :param request: HTTP GET Request
    :param uid: base64 encoded UID of user
    :param token: Token created by PasswordResetTokenGenerator
    :return: A basic HTML page that informs the user of a successful or unsuccessful activation
    """
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
