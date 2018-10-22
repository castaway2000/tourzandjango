from rest_framework import serializers
from ..models import *
from users.api.serializers import UserDetailsSerializerCustom

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class PaymentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = '__all__'

    def update(self, instance, validated_data):
        allowed_fields = ["name", "is_default", "is_active", ]
        for attr, value in validated_data.items():
            if attr in allowed_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class PaymentMethodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodType
        fields = '__all__'