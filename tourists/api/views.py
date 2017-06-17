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
from orders.models import Order


class TouristProfileViewSet(viewsets.ModelViewSet):
    queryset = TouristProfile.objects.all()
    serializer_class = TouristProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'guideprofile'):
            orders = user.guideprofile.order_set.all()
            user_ids_orders = [item.tourist.user.id for item in orders]
            qs = TouristProfile.objects.filter(Q(user=user)|Q(user_id__in=user_ids_orders))
        else:
            qs = TouristProfile.objects.filter(Q(user=user))
        return qs


class TouristTravelPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TouristTravelPhoto.objects.all()
    serializer_class = TouristTravelPhotoSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        user = self.request.user
        qs = TouristTravelPhoto.objects.filter(user=user)
        return qs
