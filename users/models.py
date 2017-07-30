from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.internalization_wrapper import languages_english
from django.db.models.signals import post_save
from utils.disabling_signals_for_load_data import disable_for_loaddata
from tourists.models import TouristProfile
from utils.uploadings import upload_path_handler_user_scanned_docs
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.signals import user_logged_in


def user_login_function(sender, user, **kwargs):
    """
    A signal receiver which performs some actions for
    the user logging in.
    """
    general_profile, created = GeneralProfile.objects.get_or_create(user=user, user__is_active=True)
    if general_profile:
        pass

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
    is_trusted = models.BooleanField(default=False)
    facebook = models.CharField(max_length=64, blank=True, null=True, default=None)
    twitter = models.CharField(max_length=64, blank=True, null=True, default=None)
    google = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone_is_validated = models.BooleanField(default=False)

    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    city = models.CharField(max_length=64, blank=True, null=True, default=None)
    address = models.CharField(max_length=128, blank=True, null=True, default=None)
    address_full = models.CharField(max_length=256, blank=True, null=True, default=None)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username


def socialaccount_post_save(sender, instance, **kwargs):
    print ("socialaccount_post_save")
    user = instance.user
    provider = instance.provider
    print (user)
    print(provider)

    if user:
        general_profile, created = GeneralProfile.objects.get_or_create(user=user, user__is_active=True)

        #remake it later in more dynamic way if it is needed
        if provider == "facebook" and general_profile.facebook != instance.uid:
            general_profile.facebook = instance.uid
            general_profile.save(force_update=True)

        elif provider == "google" and general_profile.google != instance.uid:
            general_profile.google = instance.uid
            general_profile.save(force_update=True)

        elif provider == "twitter" and general_profile.twitter != instance.uid:
            general_profile.twitter = instance.uid
            general_profile.save(force_update=True)


post_save.connect(socialaccount_post_save, sender=SocialAccount)


class DocumentType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class ScanStatus(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class DocumentScan(models.Model):
    general_profile = models.ForeignKey(GeneralProfile, blank=True, null=True, default=None)
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, default=None)
    file = models.FileField(upload_to=upload_path_handler_user_scanned_docs, blank=True, null=True, default=None)
    status = models.ForeignKey(ScanStatus, blank=True, null=True, default=1)#status "new"
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.document_type:
            return "%s %s" % (self.general_profile.user.username, self.document_type.name)
        else:
            return "%s" % self.general_profile.user.username


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

