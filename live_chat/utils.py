from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from urllib.parse import urlparse, parse_qs
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from django.db import close_old_connections


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        """
        This middleware is for socket calls.
        It handles tokens from header and from query parametr of url.
        Adding jwt token to a query parameter in url is the easiest way.

        Example for chat call to sockets:
        url: ws://localhost:8002/ws/chat/84a5f8f3-17f8-4113-ac37-a04ff70a6188/?token=someLongJwtTokenFromDjangoRestFrameworkJWT
        body:
        {"message": "some test message", "chat_uuid": "84a5f8f3-17f8-4113-ac37-a04ff70a6188 (some chat uuid"}
        """
        headers = dict(scope['headers'])
        query_string = scope["query_string"] if "query_string" in scope else None
        parsed_query_string = parse_qs(query_string.decode())
        token_name = None
        token_key = parsed_query_string.get("token")
        if token_key:
            token_key = token_key[0]
            token_name = "token"
        elif b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()

        if token_name and token_key:
            try:
                if token_name.lower() == 'token':
                    """
                    if use permanent token instead of jwt
                    """
                    # token = Token.objects.get(key=token_key)
                    # scope['user'] = token.user
                    # print(token.user)

                    """
                    if use jwt token
                    """
                    data = {'token': token_key}
                    valid_data = VerifyJSONWebTokenSerializer().validate(data)
                    user = valid_data['user']
                    scope['user'] = user
                    close_old_connections()

            except Exception as e:
                # scope['user'] = AnonymousUser()
                error_message = "Error with request %s" % str(e)
                raise ValueError(error_message)

        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))