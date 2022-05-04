"""
General web socket middleware
"""
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from accounts.models import Account
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from urllib.parse import parse_qs
from jwt import decode as jwt_decode
from django.conf import settings


@database_sync_to_async
def get_user(validated_token):
    """
    Retrieve user from database based on validated JWT token.

    :param validated_token: JWT token that is valid
    :return: User the owns the token or AnonymousUser if not found
    """
    try:
        user = get_user_model().objects.get(id=validated_token["user_id"])
        return user

    except Account.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate user when opening a websocket connection.
    """
    def __init__(self, inner):
        super().__init__(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """
        Authenticate user before moving on to the parent call method.
        """
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        try:
            # Get the token
            token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        except KeyError:
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError):
            # Token is invalid
            await send({
                "type": "websocket.accept"}
            )
            await send({
                "type": "websocket.send",
                "text": "{\"errors\": [\"Token is invalid or expired\"]}"}
            )
            await send({
                "type": "websocket.close"}
            )
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }

            # Get the user using ID
            scope["user"] = await get_user(validated_token=decoded_data)
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    """
    Return an instance of the JWTAuth middleware.
    """
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))