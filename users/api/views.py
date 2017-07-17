from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.authtoken.models import Token

from rest_framework import viewsets
from ..models import *
from .serializers import *
from .permissions import IsUserOwnerOrReadOnly


class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserInterestViewSet(viewsets.ModelViewSet):
    queryset = UserInterest.objects.all()
    serializer_class = UserInterestSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)


class LanguageLevelViewSet(viewsets.ModelViewSet):
    queryset = LanguageLevel.objects.all()
    serializer_class = LanguageLevelSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class UserLanguageViewSet(viewsets.ModelViewSet):
    queryset = UserLanguage.objects.all()
    serializer_class = UserLanguageSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)


##Reference http://polyglot.ninja/django-rest-framework-authentication-permissions/
##use this for clients token creation
@api_view(["POST"])
def login_api_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Login failed"}, status=HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["POST"])
def signup_api_view(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")

    if User.objects.filter(username=username).exists():
        return Response({"error": "Signup failed: such username exists"}, status=HTTP_401_UNAUTHORIZED)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Signup failed: such email already exists"}, status=HTTP_401_UNAUTHORIZED)

    if password1 != password2:
        return Response({"error": "Signup failed: passwords do not match"}, status=HTTP_401_UNAUTHORIZED)

    user = User.objects.create_user(username=username, email=email, password=password1)
    if not user:
        return Response({"error": "Signup failed during creation a new user"}, status=HTTP_401_UNAUTHORIZED)


    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})
