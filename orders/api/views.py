from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from ..models import *
from .serializers import *
from .permissions import IsTouristOwnerOrReadOnly, IsTouristOrGuideOwnerOrReadOnly

from django.db.models import Q
from django.shortcuts import get_object_or_404
from utils.api_helpers import FilterViewSet
import django_filters


class OrderStatusViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = OrderStatus.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class ServiceInOrderViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = ServiceInOrder.objects.all()
    serializer_class = ServiceInOrderSerializer
    permission_classes = (IsAuthenticated, IsTouristOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        qs = ServiceInOrder.objects.filter(Q(order__guide__user=user)|Q(order__tourist__user=user))
        return qs


# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ('get',)
#
#     def get_queryset(self):
#         user = self.request.user
#         qs = ServiceInOrder.objects.filter(Q(order__guide__user=user)|Q(order__tourist__user=user))
#         return qs


class ReviewFilter(django_filters.FilterSet):
    tourist_user_id = django_filters.NumberFilter(name='order__tourist__user_id')
    guide_user_id = django_filters.NumberFilter(name='order__guide__user_id')
    class Meta:
        model = Review
        fields = {
            'tourist_user_id': ['exact'],
            'guide_user_id': ['exact'],
            'guide_rating': ['exact', 'gte', 'lte'],
            'tourist_rating': ['exact', 'gte', 'lte'],
            'is_guide_feedback': ['exact'],
            'is_tourist_feedback': ['exact'],
        }


class ReviewViewSet(viewsets.ModelViewSet):
    #Improve for later: to limit fields which can be modified by guide and tourist because both
    #of their feedbacks are stored on the same line

    #Example for filtering by tourist user id: http://localhost:8000/api/v1/reviews?tourist_user_id=29
    #Example for filtering by guide user id: http://localhost:8000/api/v1/reviews?guide_user_id=30
    #Example for filtering by guide user id and guide score http://localhost:8000/api/v1/reviews?guide_user_id=30&guide_rating__lte=4
    #By guide score we mean a score, put by a guide to a tourist
    #lte - less than or equal
    #gte - greater than or equal

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny, IsTouristOrGuideOwnerOrReadOnly,)
    filter_class = ReviewFilter
    filter_fields = ("tourist_user_id",)

    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = Review.objects.filter(order__tourist__user=user, is_tourist_feedback=True).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_guide_representation(self, request):
        #requires logged in user
        user = request.user
        qs = Review.objects.filter(order__guide__user=user, is_guide_feedback=True).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet, FilterViewSet):
    #add later a logic to permissions for not allowing modify completed orders
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(Q(guide__user=user)|Q(tourist__user=user))
        return qs

    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = Order.objects.filter(tourist__user=user).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_guide_representation(self, request):
        user = request.user
        qs = Order.objects.filter(guide__user=user).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
