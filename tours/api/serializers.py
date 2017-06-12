from rest_framework import serializers
from tours.models import *
from orders.models import Order, Review
from orders.api.serializers import OrderSerializer, ReviewSerializer
from chats.api.serializers import ChatSerializer


"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class PaymentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentType
        fields = '__all__'


class TourSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(source='order_set', many=True)
    reviews = serializers.SerializerMethodField()#this field searches for the function "get_"+field_name
    chats = ChatSerializer(source='chat_set', many=True)

    class Meta:
        model = Tour
        fields = '__all__'

    def get_reviews(self, obj):
        # values = obj.get_values() # whatever your filter values are. obj is the current instance (Tour)
        # tour_ids = [tour["id"] for tour in obj]
        tour = obj
        reviews = Review.objects.filter(order__tour=tour) # Or whatever queryset filter
        return ReviewSerializer(reviews, many=True).data


class TourImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TourImage
        fields = '__all__'