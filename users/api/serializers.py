from rest_framework import serializers
from ..models import *
from rest_auth.serializers import UserDetailsSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, UserModel
from allauth.account.forms import ResetPasswordForm, SetPasswordForm

"""
Good references:
http://www.django-rest-framework.org/api-guide/serializers/#specifying-nested-serialization
http://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework
"""

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    interest = InterestSerializer()

    class Meta:
        model = UserInterest
        fields = '__all__'


class LanguageLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageLevel
        fields = '__all__'


class UserLanguageSerializer(serializers.ModelSerializer):
    level = LanguageLevelSerializer()

    class Meta:
        model = UserLanguage
        fields = '__all__'


class GeneralProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneralProfile
        fields = '__all__'


class GeneralProfileForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneralProfile
        fields = ('phone', 'phone_is_validated', 'registration_country', 'registration_state', 'registration_city', 'registration_street',
                  'registration_building_nmb', 'registration_flat_nmb', 'registration_postcode',)



#
# user_obj = {'user_id': user.id,
#                 'username': user.username,
#                 'email': user.email,
#                 'phone': user.generalprofile.phone,
#                 'building_num': user.generalprofile.registration_building_nmb,
#                 'flat_num': user.generalprofile.registration_flat_nmb,
#                 'street': user.generalprofile.registration_street,
#                 'city': user.generalprofile.registration_city,
#                 'state': user.generalprofile.registration_state,
#                 'country': user.generalprofile.registration_country,
#                 'postcode': user.generalprofile.registration_postcode,
#                 # 'interests': user.userinterest_set.all(),
#                 'guide_id': guide_id,
#                 # 'profile_pic': tourist_image,
#                 }



class UserDetailsSerializerCustom(UserDetailsSerializer):
    """
    User model w/o password
    """
    interests = UserInterestSerializer(source="userinterest_set", many=True, required=False)
    general_profile = GeneralProfileForUserSerializer(source="generalprofile", required=False)
    guide_id = serializers.SerializerMethodField()
    guide_profile_image = serializers.SerializerMethodField()
    tourist_profile_image = serializers.SerializerMethodField()

    def get_guide_id(self, model_obj):
        guide_id = model_obj.guideprofile.id if hasattr(model_obj, "guideprofile") else None
        return guide_id

    def get_guide_profile_image(self, model_obj):
        image_url = model_obj.guideprofile.profile_image.url if hasattr(model_obj, "guideprofile") else None
        return image_url

    def get_tourist_profile_image(self, model_obj):
        image_url = model_obj.touristprofile.image.url if hasattr(model_obj, "touristprofile") else None
        return image_url

    class Meta:
        model = UserModel
        fields = ('pk', 'username', 'email', 'guide_id', 'guide_profile_image', 'tourist_profile_image', 'general_profile', 'interests',)
        read_only_fields = ('email', )


class PasswordResetSerializerCustom(PasswordResetSerializer):
    password_reset_form_class = ResetPasswordForm


class PasswordResetConfirmSerializerCustom(PasswordResetConfirmSerializer):
    set_password_form_class = SetPasswordForm




