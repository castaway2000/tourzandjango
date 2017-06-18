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


class OrderStatusViewSet(viewsets.ModelViewSet):
    queryset = OrderStatus.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class ServiceInOrderViewSet(viewsets.ModelViewSet):
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


class ReviewViewSet(viewsets.ModelViewSet):
    #Improve for later: to limit fields which can be modified by guide and tourist because both
    #of their feedbacks are stored on the same line

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny, IsTouristOrGuideOwnerOrReadOnly,)


    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = Review.objects.filter(order__tourist__user=user, is_tourist_feedback=True).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_guide_representation(self, request):
        user = request.user
        qs = Review.objects.filter(order__guide__user=user, is_guide_feedback=True).order_by('-id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
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
