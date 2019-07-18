from rest_framework import serializers
from ..models import *
from users.api.serializers import UserDetailsSerializerCustom

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
    user_tourist = serializers.SerializerMethodField()
    user_guide = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_user_tourist(self, model_obj):
        #get just model_obj.order.tourist bellow in case of a need to show "Tourist" object instead of user object
         #and user TouristProfileSerializer instead of UserDetailsSerializerCustom
        tourist_user_obj = [model_obj.order.tourist.user if hasattr(model_obj, "order") else None]
        return UserDetailsSerializerCustom(tourist_user_obj, many=True).data

    def get_user_guide(self, model_obj):
        #get just model_obj.order.tourist bellow in case of a need to show "Guide" object instead of user object
        #and user GuideProfileSerializer instead of UserDetailsSerializerCustom
        tourist_user_obj = model_obj.order.guide.user if hasattr(model_obj, "order") else None
        return UserDetailsSerializerCustom(tourist_user_obj, many=False).data

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
    reviews = ReviewSerializer(source='review')

    class Meta:
        model = Order
        fields = '__all__'



