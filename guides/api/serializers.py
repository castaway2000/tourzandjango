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


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class GuideServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideService
        fields = '__all__'


class GuideProfileSerializer(serializers.ModelSerializer):
    guide_services = GuideServiceSerializer(source='guideservice_set', many=True, required=False)
    tours = TourSerializer(source='tour_set', many=True)#specify source if it is different from field name
    interests = UserInterestSerializer(source='user.userinterest_set', many=True, required=False)
    languages = UserLanguageSerializer(source='user.userlanguage_set', many=True, required=False)
    # orders = OrderSerializer(source='order_set', many=True, required=False)
    # reviews = serializers.SerializerMethodField(required=False)#this field searches for the function "get_"+field_name
    # chats = ChatSerializer(source='user.guide', many=True, required=False)

    class Meta:
        model = GuideProfile
        fields = '__all__'

    def get_reviews(self, obj):
        guide = obj
        reviews = Review.objects.filter(order__guide=guide) # Or whatever queryset filter
        return ReviewSerializer(reviews, many=True).data


class GuideProfileBasicSerializer(serializers.ModelSerializer):
    guide_services = GuideServiceSerializer(source='guideservice_set', many=True, required=False)
    interests = UserInterestSerializer(source='user.userinterest_set', many=True, required=False)
    languages = UserLanguageSerializer(source='user.userlanguage_set', many=True, required=False)

    class Meta:
        model = GuideProfile
        fields = '__all__'



#serializers examples for cases with generic views
"""
class GuideProfileCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideProfile
        fields = [

        ]


post_detail_url = serializers.HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='slug'
        )


class GuideProfileDetailSerializer(serializers.ModelSerializer):
    # url = post_detail_url
    # user = UserDetailSerializer(read_only=True)
    # image = SerializerMethodField()
    # html = SerializerMethodField()
    # comments = SerializerMethodField()
    class Meta:
        model = GuideProfile
        fields = [

        ]

    def get_html(self, obj):
        return obj.get_markdown()

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image

    # def get_comments(self, obj):
    #     c_qs = Comment.objects.filter_by_instance(obj)
    #     comments = CommentSerializer(c_qs, many=True).data
    #     return comments



class GuideProfileListSerializer(serializers.ModelSerializer):
    # url = post_detail_url
    # user = UserDetailSerializer(read_only=True)
    class Meta:
        model = GuideProfile
        fields = [

        ]
"""