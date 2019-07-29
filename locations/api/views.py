from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from ..models import *
from .serializers import *
from utils.api_helpers import FilterViewSet


class LocationTypeViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)


class LocationViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'create',)


class CityViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'create',)

class CountryViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'create',)


class CurrencyViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
