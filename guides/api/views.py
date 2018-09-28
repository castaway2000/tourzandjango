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
from .filters import GuideFilter

from .serializers import *
from rest_framework import viewsets

from guides.models import *
from utils.api_helpers import FilterViewSet

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from ..models import GuideProfile, GuideService
from users.models import UserInterest, UserLanguage


class GuideProfileViewSet(viewsets.ModelViewSet):
    queryset = GuideProfile.objects.filter(is_active=True)
    serializer_class = GuideProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    http_method_names = ['get', 'create']
    filter_class = GuideFilter


    @list_route()
    def get_tourist_representation(self, request):
        #This is a representation of guides profiels for guides list page
        #complicated filter logic is here less complicated such as "exact", "lte", "gte" is in a separate self.filter_class

        #API call example for filtering guides with the rate 10 USD:
        #  http://localhost:8000/api/v1/guides/get_tourist_representation/?rate=10

        #API call example for filtering guides with the rate greater than or equal to 20 USD and interests with
        # at least one item from these two: coding or traveling:
        #http://localhost:8000/api/v1/guides/get_tourist_representation/?rate__gte=20&interests=["coding", "traveling"]

        self.serializer_class = GuideProfileBasicSerializer#less nested fields for this representation
        data = request.GET
        kwargs = {
            "is_active": True
        }
        user_ids_to_filter = list()
        interests = data.get("interests")
        print(interests)
        if interests:
            user_interests = UserInterest.objects.filter(interest__name__in=interests).values("user")
            user_ids = [item["user"] for item in user_interests]
            user_ids_to_filter.extend(user_ids)
        languages = data.get("languages")
        if languages:
            user_languages = UserLanguage.objects.filter(language__name__in=languages).values("user")
            user_ids = [item["user"] for item in user_languages]
            user_ids_to_filter.extend(user_ids)
        services = data.get("services")
        if services:
            guide_services = UserLanguage.objects.filter(language__name__in=languages).values("guide__user")
            user_ids = [item["guide__user"] for item in guide_services]
            user_ids_to_filter.extend(user_ids)

        is_include_corporate = data.get("include_corporate")
        if is_include_corporate:
            kwargs["user__generalprofile__is_company"] = True
        else:
            kwargs["user__generalprofile__is_company"] = False

        if len(user_ids_to_filter)>0:
            kwargs["user_id__in"]=user_ids_to_filter

        location = data.get("location")
        if location:
            q_objects = Q()

            main_filters_for_city = kwargs.copy()
            main_filters_for_city.update({"city__name": location})
            q_objects |= Q(**main_filters_for_city)

            main_filters_for_country = kwargs.copy()
            main_filters_for_country.update({"city__country__name": location})
            q_objects |= Q(**main_filters_for_country)

            qs = self.get_queryset().filter(q_objects).order_by('-id')
        else:
            print(kwargs)
            qs = self.get_queryset().filter(**kwargs).order_by('-id')
        qs = self.filter_queryset(qs)#it allows to use combination of filters in this view and in filter_class
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet, FilterViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class GuideServiceViewSet(viewsets.ModelViewSet, FilterViewSet):
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