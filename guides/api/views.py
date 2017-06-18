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
from .permissions import IsOwnerOrReadOnly, IsGuideOwnerOrReadOnly

from .serializers import *
from rest_framework import viewsets

from guides.models import *


class GuideProfileViewSet(viewsets.ModelViewSet):
    queryset = GuideProfile.objects.all()
    serializer_class = GuideProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class GuideServiceViewSet(viewsets.ModelViewSet):
    queryset = GuideService.objects.all()
    serializer_class = GuideServiceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsGuideOwnerOrReadOnly,)


"""
possible ways as well
"""
# class GuideProfileCreateAPIView(CreateAPIView):
#     queryset = GuideProfile.objects.all()
#     serializer_class = GuideProfileCreateUpdateSerializer
#     #permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#
#
# class GuideProfileUpdateAPIView(RetrieveUpdateAPIView):
#     queryset = GuideProfile.objects.all()
#     serializer_class = GuideProfileCreateUpdateSerializer
#     # lookup_field = 'slug'
#     permission_classes = [IsOwnerOrReadOnly]
#     #lookup_url_kwarg = "abc"
#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)
#
#
# class GuideProfileDeleteAPIView(DestroyAPIView):
#     queryset = GuideProfile.objects.all()
#     serializer_class = GuideProfileDetailSerializer
#     lookup_field = 'slug'
#     permission_classes = [IsOwnerOrReadOnly]
#     #lookup_url_kwarg = "abc"
#
#
#
# class GuideProfileDetailAPIView(RetrieveAPIView):
#     queryset = GuideProfile.objects.all()
#     serializer_class = GuideProfileDetailSerializer
#     # lookup_field = 'slug'
#     permission_classes = [AllowAny]
#     #lookup_url_kwarg = "abc"
#
#
# class GuideProfileListAPIView(ListAPIView):
#     serializer_class = GuideProfileListSerializer
#     filter_backends= [SearchFilter, OrderingFilter]
#     permission_classes = [AllowAny]
#     # search_fields = ['title', 'content', 'user__first_name']
#     pagination_class = PostPageNumberPagination #PageNumberPagination
#
#     def get_queryset(self, *args, **kwargs):
#         #queryset_list = super(PostListAPIView, self).get_queryset(*args, **kwargs)
#         queryset_list = GuideProfile.objects.all() #filter(user=self.request.user)
#         query = self.request.GET.get("q")
#         if query:
#             queryset_list = queryset_list.filter(
#                     Q(title__icontains=query)|
#                     Q(content__icontains=query)|
#                     Q(user__first_name__icontains=query) |
#                     Q(user__last_name__icontains=query)
#                     ).distinct()
#             return queryset_list