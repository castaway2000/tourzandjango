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


class ContactUsMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactUsMessage.objects.all()
    serializer_class = ContactUsMessageSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post',)
