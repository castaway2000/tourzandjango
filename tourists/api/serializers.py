"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""

from rest_framework import serializers
from ..models import *
from tours.api.serializers import TourSerializer
from users.api.serializers import UserInterestSerializer, UserLanguageSerializer
from orders.api.serializers import OrderSerializer, ReviewSerializer
from chats.api.serializers import ChatSerializer

from orders.models import Review


class TouristProfileSerializer(serializers.ModelSerializer):
    interests = UserInterestSerializer(source='user.userinterest_set', many=True)
    languages = UserLanguageSerializer(source='user.userlanguage_set', many=True)

    orders = OrderSerializer(source='order_set', many=True)
    reviews = serializers.SerializerMethodField()
    chats = ChatSerializer(source='user.tourist', many=True)

    class Meta:
        print("im in")
        model = TouristProfile
        fields = '__all__'

    def get_reviews(self, obj):
        tourist = obj
        reviews = Review.objects.filter(order__tourist=tourist) # Or whatever queryset filter
        return ReviewSerializer(reviews, many=True).data


class TouristTravelPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristTravelPhoto
        fields = '__all__'
