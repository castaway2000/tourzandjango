from rest_framework import serializers
from ..models import *

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""


class BlogCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogCategory
        fields = '__all__'


class BlogTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogTag
        fields = '__all__'


class BlogPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPost
        fields = '__all__'


class BlogPostTagSerializer(serializers.ModelSerializer):

    class Meta:
        model =  BlogPostTag
        fields = '__all__'
