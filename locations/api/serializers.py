from rest_framework import serializers
from ..models import *

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class LocationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationType
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    interest = LocationTypeSerializer()

    class Meta:
        model = Location
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = '__all__'