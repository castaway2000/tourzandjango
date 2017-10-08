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


class GeneralProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    is_trusted = models.BooleanField(default=False) #is trusted by connection social networks, phone, validation of address
    is_verified = models.BooleanField(default=False)#is verified by docs
    webcam_image = models.ImageField(upload_to=upload_path_handler_guide_webcam_image, blank=True, null=True, default=None)

    facebook = models.CharField(max_length=64, blank=True, null=True, default=None)
    twitter = models.CharField(max_length=64, blank=True, null=True, default=None)
    google = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone_is_validated = models.BooleanField(default=False)
    phone_pending = models.CharField(max_length=64, blank=True, null=True, default=None)

    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    city = models.CharField(max_length=64, blank=True, null=True, default=None)
    address = models.CharField(max_length=128, blank=True, null=True, default=None)
    address_full = models.CharField(max_length=256, blank=True, null=True, default=None)

    is_company = models.BooleanField(default=False)
    business_id = models.CharField(max_length=64, blank=True, null=True, default=None)

    is_previously_logged_in = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username

    def save(self, *args, **kwargs):
        self.address_full = "%s %s" % (self.city, self.address)

        super(GeneralProfile, self).save(*args, **kwargs)



def socialtoken_post_save(sender, instance, **kwargs):
    # print("social token post save")
    social_account = instance.account
    user = social_account.user
    provider = social_account.provider

    if user:
        general_profile, created = GeneralProfile.objects.get_or_create(user=user, user__is_active=True)

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