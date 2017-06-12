from django.db.models import Q

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
    )

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )

from rest_framework.viewsets import (
    ReadOnlyModelViewSet,

)

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination
from .permissions import IsOwnerOrReadOnly

from .serializers import *
from rest_framework import viewsets

from ..models import *


class TouristProfileViewSet(viewsets.ModelViewSet):
    queryset = TouristProfile.objects.all()
    serializer_class = TouristProfileSerializer
    permission_classes = (AllowAny,)


class TouristTravelPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TouristTravelPhoto.objects.all()
    serializer_class = TouristTravelPhotoSerializer
    permission_classes = (AllowAny,)
