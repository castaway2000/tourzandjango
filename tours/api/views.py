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
from .permissions import IsGuideOwnerOrReadOnly, IsTourGuideOwnerOrReadOnly


class PaymentTypeViewSet(viewsets.ModelViewSet):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = (IsGuideOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        qs = Tour.objects.filter(is_active=False, is_deleted=False)
        return qs

    @list_route()
    def get_guide_representation(self, request):
        user = request.user
        qs = Tour.objects.filter(guide__user=user).order_by('-id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TourImageViewSet(viewsets.ModelViewSet):
    queryset = TourImage.objects.all()
    serializer_class = TourImageSerializer
    permission_classes = (IsTourGuideOwnerOrReadOnly,)