from rest_framework import serializers
from ..models import *

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderStatus
        fields = '__all__'


class ServiceInOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceInOrder
        fields = '__all__'


# class PaymentSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Payment
#         fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'


    def update(self, instance, validated_data):

        if instance.order.tourist.user:
            print ("USER: %s" % instance.order.tourist.user)
            # instance.email = validated_data.get('email', instance.email)
            # instance.content = validated_data.get('content', instance.content)
            # instance.created = validated_data.get('created', instance.created)
        return instance


class OrderSerializer(serializers.ModelSerializer):
    services = ServiceInOrderSerializer(source='serviceinorder_set', many=True)
    # payments = PaymentSerializer(source='payment_set', many=True)
    reviews = ReviewSerializer(source='review_set', many=True)

    class Meta:
        model = Order
        fields = '__all__'



