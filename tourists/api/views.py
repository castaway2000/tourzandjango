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

from rest_framework import viewsets
from .serializers import *
from .permissions import IsUserOwnerOrReadOnly

from ..models import *
from chats.models import Chat


class TouristProfileViewSet(viewsets.ModelViewSet):
    queryset = TouristProfile.objects.all()
    serializer_class = TouristProfileSerializer
    permission_classes = (IsUserOwnerOrReadOnly,)

    def get_queryset(self):
        print("get queryset")
        user = self.request.user
        print(user)
        if not user.is_anonymous():
            print (user)
            #showing only tourist if the current tourist is guide and he has orders with a tourist or a chat
            if hasattr(user, 'guideprofile'):
                print("guideprofile")
                orders = user.guideprofile.order_set.all()
                user_ids_orders = [item.tourist.user_id for item in orders]

                chats = Chat.objects.filter(guide=user)
                chat_tourist_user_ids = [item.tourist.id for item in chats]
                qs = TouristProfile.objects.filter(Q(user=user)|Q(user_id__in=user_ids_orders)|Q(user_id__in=chat_tourist_user_ids))
                print(qs)
            else:
                qs = TouristProfile.objects.filter(user=user)
            return qs


class TouristTravelPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TouristTravelPhoto.objects.all()
    serializer_class = TouristTravelPhotoSerializer
    permission_classes = (IsUserOwnerOrReadOnly, )

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous():
            qs = TouristTravelPhoto.objects.filter(user=user)
            return qs
