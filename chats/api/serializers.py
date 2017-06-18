from rest_framework import serializers
from ..models import *

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(source='chatmessage_set', many=True, required=False)

    class Meta:
        model = Chat
        fields = '__all__'
        read_only_fields = ('messages',)
