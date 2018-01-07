from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.internalization_wrapper import languages_english
from django.db.models.signals import post_save
from utils.disabling_signals_for_load_data import disable_for_loaddata
from tourists.models import TouristProfile
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.signals import user_logged_in
from payments.models import PaymentMethod
from phonenumber_field.modelfields import PhoneNumberField
from guides.models import GuideProfile
from utils.uploadings import upload_path_handler_guide_webcam_image
import pycountry
from datetime import date


def user_login_function(sender, user, **kwargs):
    """
    A signal receiver which performs some actions for
    the user logging in.
    """
    general_profile, created = GeneralProfile.objects.get_or_create(user=user)
    if not general_profile.is_trusted:
        is_trust_score = 0

        if general_profile.facebook or general_profile.google or general_profile.twitter:
            is_trust_score += 1

        if general_profile.phone and general_profile.phone_is_validated:
            is_trust_score += 1

        if general_profile.documentscan_set.filter(status_id=2).exists():
            is_trust_score += 1

        if PaymentMethod.objects.filter(user=user, is_active=True).exists():
            is_trust_score += 1

        if is_trust_score >= 3:
            general_profile.is_trusted = True
        # else:
        #     general_profile.is_trusted = False
        general_profile.save(force_update=True)


user_logged_in.connect(user_login_function)


"""
creating user profile after user is created (mostly for login with Facebook)
"""
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        kwargs = dict()
        kwargs["user"] = instance
        TouristProfile.objects.create(**kwargs)

post_save.connect(create_user_profile, sender=User)


class Interest(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class UserInterest(models.Model):
    user = models.ForeignKey(User)
    interest = models.ForeignKey(Interest)

    def __str__(self):
        if self.interest.name:
            return "%s" % self.interest.name
        else:
            return "%s" % self.interest.id


class LanguageLevel(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class UserLanguage(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    language = models.CharField(max_length=8, choices=languages_english, null=True)
    level = models.ForeignKey(LanguageLevel, blank=True, null=True, default=1)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.language


COUNTRY_CHOICES = ((country.name, country.name) for country in pycountry.countries )

class GeneralProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=0)
    profession = models.CharField(max_length=256, blank=True, null=True)

    is_trusted = models.BooleanField(default=False) #is trusted by connection social networks, phone, validation of address
    is_verified = models.BooleanField(default=False)#is verified by docs
    webcam_image = models.ImageField(upload_to=upload_path_handler_guide_webcam_image, blank=True, null=True, default=None)

    facebook = models.CharField(max_length=64, blank=True, null=True, default=None)
    twitter = models.CharField(max_length=64, blank=True, null=True, default=None)
    google = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone_is_validated = models.BooleanField(default=False)
    phone_pending = models.CharField(max_length=64, blank=True, null=True, default=None)

    registration_country = models.CharField(max_length=256, blank=True, null=True, choices=COUNTRY_CHOICES)
    registration_country_ISO_3_digits = models.CharField(max_length=8, blank=True, null=True)
    registration_state = models.CharField(max_length=256, blank=True, null=True)
    registration_city = models.CharField(max_length=256, blank=True, null=True)
    registration_street = models.CharField(max_length=256, blank=True, null=True)
    registration_building_nmb = models.CharField(max_length=256, blank=True, null=True)
    registration_flat_nmb = models.CharField(max_length=256, blank=True, null=True)
    registration_postcode = models.CharField(max_length=256, blank=True, null=True)

    is_company = models.BooleanField(default=False)
    business_id = models.CharField(max_length=64, blank=True, null=True, default=None)

    is_previously_logged_in = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __init__(self, *args, **kwargs):
        super(GeneralProfile, self).__init__(*args, **kwargs)
        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def __str__(self):
        return "%s" % self.user.username

    def save(self, *args, **kwargs):

        if not self.pk or self.registration_country != self._original_fields["registration_country"]:
            if self.registration_country:
                self.registration_country_ISO_3_digits = pycountry.countries.get(name=self.registration_country).alpha_3

        if self.date_of_birth:
            today = date.today()
            date_of_birth = self.date_of_birth

            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            self.age = age

        super(GeneralProfile, self).save(*args, **kwargs)


def general_profile_post_save(sender, instance, **kwargs):
    if hasattr(instance.user, "guideprofile"):
        guide = instance.user.guideprofile
        guide.name = instance.first_name
        guide.save(force_update=True)
post_save.connect(general_profile_post_save, sender=GeneralProfile)


def socialtoken_post_save(sender, instance, **kwargs):
    # print("social token post save")
    social_account = instance.account
    user = social_account.user
    provider = social_account.provider

    if user:
        general_profile, created = GeneralProfile.objects.get_or_create(user=user)

        #code for twitter and google authentication when no accounts and users should be created, is placed to
        #pre_social_login function of users.adapter_allAuth.MySocialAccountAdapter
        if provider == "facebook" and general_profile.facebook != social_account.uid:
            general_profile.facebook = social_account.uid
            general_profile.save(force_update=True)

post_save.connect(socialtoken_post_save, sender=SocialToken)


class SmsSendingHistory(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)#including code
    sms_code = models.CharField(max_length=8, blank=True, null=True, default=None)
    tries_nmb = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.phone
