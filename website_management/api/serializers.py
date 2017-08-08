from rest_framework import serializers
from ..models import *

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""

class ContactUsMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsMessage
        fields = ("name", "email", "message",)


    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_anonoymous():
            serializer.save(user=user)
        else:
            serializer.save()