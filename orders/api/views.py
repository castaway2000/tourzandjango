from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.core import serializers as serial
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from django.http import HttpResponse

from ..models import *
from .serializers import *
from .permissions import IsTouristOwnerOrReadOnly, IsTouristOrGuideOwnerOrReadOnly

from django.db.models import Q
from django.shortcuts import get_object_or_404
from utils.api_helpers import FilterViewSet
from .filters import ReviewFilter

import json


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


class ReviewViewSet(viewsets.ModelViewSet):
    #Improve for later: to limit fields which can be modified by guide and tourist because both
    #of their feedbacks are stored on the same line

    #Example for filtering by tourist user id: http://localhost:8000/api/v1/reviews/?tourist_user_id=29
    #Example for filtering by guide user id: http://localhost:8000/api/v1/reviews/?guide_user_id=30
    #Example for filtering by guide user id and guide score http://localhost:8000/api/v1/reviews/?guide_user_id=30&guide_rating__lte=4
    #By guide score we mean a score, put by a guide to a tourist
    #lte - less than or equal
    #gte - greater than or equal

    #Example of filtering by tourist user id for guide representation (TO DO IT ONLY WITH AUTH TOKEN for having logged in user)
    #Example for filtering by tourist user id: http://localhost:8000/api/v1/reviews/get_guide_representation?tourist_user_id=29

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny, IsTouristOrGuideOwnerOrReadOnly,)
    filter_class = ReviewFilter

    @list_route()
    def get_tourist_representation(self, request):
        user = request.user
        qs = self.get_queryset().filter(order__tourist__user=user, is_tourist_feedback=True).order_by('-id')
        qs = self.filter_queryset(qs)#it allows to use combination of filters in this view and in filter_class
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def get_guide_representation(self, request):
        #requires logged in user
        user = request.user
        qs = self.get_queryset().filter(order__guide__user=user, is_guide_feedback=True).order_by('-id')
        qs = self.filter_queryset(qs)#it allows to use combination of filters in this view and in filter_class
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def create_review(self, request, *args, **kwargs):
        data = request.GET
        Review.objects.get_or_create(order_id=data['order'])
        review = Review.objects.get(order_id=data['order'])
        dt = datetime.datetime.now()
        if data['is_tourist_feedback'] == 'True':
            print('tourist review')
            review.is_tourist_feedback = True
            review.guide_feedback_name = data['guide_feedback_name']
            review.guide_feedback_text = data['guide_feedback_text']
            review.guide_rating = int(data['guide_rating'])
            if review.guide_review_created is not None:
                review.guide_review_updated = dt
            else:
                review.guide_review_created = dt
                review.guide_review_updated = dt

        if data['is_guide_feedback'] == 'True':
            print('guide review')
            review.is_guide_feedback = True
            review.tourist_feedback_name = data['tourist_feedback_name']
            review.tourist_feedback_text = data['tourist_feedback_text']
            review.tourist_rating = int(data['tourist_rating'])
            if review.tourist_review_created is not None:
                review.tourist_review_updated = dt
            else:
                review.tourist_review_created = dt
                review.tourist_review_updated = dt
        print(review)
        review.save()
        return Response({'detail': 'success'})



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
        results = []
        user = request.user
        qs = Order.objects.filter(tourist__user=user).order_by('-id')
        for q in qs:
            tourist = q.tourist.user.generalprofile.user_id
            guide = q.guide.user.generalprofile.user_id
            new_query = model_to_dict(q)
            new_query['tourist_generalprofile_id'] = tourist
            new_query['guide_generalprofile_id'] = guide
            results.append(new_query)
        return HttpResponse(json.dumps(results, cls=DjangoJSONEncoder))

    @list_route()
    def get_guide_representation(self, request):
        results = []
        user = request.user
        qs = Order.objects.filter(guide__user=user).order_by('-id')
        for q in qs:
            tourist = q.tourist.user.generalprofile.id
            guide = q.guide.user.generalprofile.id
            new_query = model_to_dict(q)
            new_query['tourist_generalprofile_id'] = tourist
            new_query['guide_generalprofile_id'] = guide
            results.append(new_query)
        return HttpResponse(json.dumps(results, cls=DjangoJSONEncoder))