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
from payments.models import PaymentMethod, Payment
from phonenumber_field.modelfields import PhoneNumberField
from guides.models import GuideProfile
from utils.uploadings import upload_path_handler_guide_webcam_image
import pycountry
from datetime import date
from utils.general import uuid_creating, uuid_size_6_creating

from django.core.cache import cache
import datetime
from tourzan.settings import USER_ONLINE_TIMEOUT


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
def user_post_save(sender, instance, created, **kwargs):
    user = instance
    GeneralProfile.objects.update_or_create(user=user, defaults={"first_name": user.first_name,
                                                                 "last_name": user.last_name})
    if created:
        kwargs = dict()
        kwargs["user"] = user
        TouristProfile.objects.create(**kwargs)
post_save.connect(user_post_save, sender=User)


class Interest(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        super(Interest, self).save(*args, **kwargs)


class UserInterest(models.Model):
    user = models.ForeignKey(User)
    interest = models.ForeignKey(Interest)
    is_active = models.BooleanField(default=True)

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
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.language


COUNTRY_CHOICES = ((country.name, country.name) for country in pycountry.countries )


class GeneralProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    uuid = models.CharField(max_length=48, null=True)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=0)
    profession = models.CharField(max_length=256, blank=True, null=True)

    referred_by = models.ForeignKey(User, blank=True, null=True, default=None, related_name="referred_by")
    referral_code = models.CharField(max_length=64, null=True, blank=True)
    tourists_referred_nmb = models.IntegerField(default=0)
    tourists_with_purchases_referred_nmb = models.IntegerField(default=0)
    guides_referred_nmb = models.IntegerField(default=0)
    guides_verified_referred_nmb = models.IntegerField(default=0)
    is_fee_free = models.BooleanField(default=False, blank=False)

    is_trusted = models.BooleanField(default=False) #is trusted by connection social networks, phone, validation of address
    is_verified = models.BooleanField(default=False)#is verified by docs
    webcam_image = models.ImageField(upload_to=upload_path_handler_guide_webcam_image, blank=True, null=True, default=None)

    facebook = models.CharField(max_length=64, blank=True, null=True, default=None)
    twitter = models.CharField(max_length=64, blank=True, null=True, default=None)
    google = models.CharField(max_length=64, blank=True, null=True, default=None)
    instagram = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone_is_validated = models.BooleanField(default=False)
    phone_pending = models.CharField(max_length=64, blank=True, null=True, default=None)
    device_id = models.CharField(blank=True, null=True, default=None, max_length=240)

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

        if (self.first_name != self.user.first_name or self.last_name != self.user.last_name) \
                and (self.first_name or self.last_name):
            if self.first_name:
                self.user.first_name = self.first_name
            if self.last_name:
                self.user.last_name = self.last_name
            self.user.save(force_update=True)

        if not self.uuid:
            self.uuid = uuid_creating()

        if not self.referral_code:
            self.referral_code = self.create_referral_code()

        #adding statistics for referrer when referred_by appears:
        if not self._original_fields["referred_by"] and self.referred_by:
            referred_by = self.referred_by
            referred_by.generalprofile.tourists_referred_nmb += 1
            referred_by.generalprofile.save(force_update=True)

        #adding statistics for referrer when guides become verified
        referred_by = self.referred_by
        if referred_by:
            if (not self._original_fields["is_verified"] or self._original_fields["is_verified"] == False) and self.is_verified == True:
                referred_by.generalprofile.guides_verified_referred_nmb += 1
            elif (self._original_fields["is_verified"] and self._original_fields["is_verified"] == True) and self.is_verified == False:
                referred_by.generalprofile.guides_verified_referred_nmb -= 1
            referred_by.generalprofile.save(force_update=True)

            #adding is_fee_free perk for generalprofile for guides, who attracted guides
            # TODO: think about making it a kind of a coupon if it will be needed
            if hasattr(referred_by, "guideprofile"):
                count_fee_free_nmb = GeneralProfile.objects.filter(is_fee_free=True).count()
                if count_fee_free_nmb <= 100: #only 100 people are allowed
                    if referred_by.generalprofile.guides_verified_referred_nmb >= 5 and referred_by.generalprofile.is_fee_free == False:
                        referred_by.generalprofile.is_fee_free = True
                        referred_by.generalprofile.save(force_update=True)
                        # TODO: add email congratulations

        super(GeneralProfile, self).save(*args, **kwargs)


    def get_name(self):
        if self.first_name:
            return self.first_name
        elif self.user:
            if self.user.first_name:
                return self.user.first_name
            else:
                return self.user.username
        else:
            return ""

    def get_default_payment_method(self):
        return PaymentMethod.objects.filter(user=self.user, is_active=True).order_by('is_default', '-id').first()

    def create_referral_code(self):
        referral_code = uuid_size_6_creating()
        if GeneralProfile.objects.filter(referral_code__iexact=referral_code).exists():
            return self.create_referral_code()
        else:
            return referral_code

    def get_languages(self):
        user_languages = UserLanguage.objects.filter(user=self.user, is_active=True)
        print(user_languages)
        #Refactor this!!!
        user_language_native = None
        user_language_second = None
        user_language_third = None
        for user_language in user_languages:
            if user_language.level_id == 1 and not user_language_native:
                user_language_native = user_language
            elif user_language_native and user_language_second:
                user_language_third = user_language
            else:
                user_language_second = user_language

        return (user_language_native, user_language_second, user_language_third)

    def last_seen(self):
        return cache.get('seen_%s' % self.user.id)

    def get_is_user_online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                         seconds=USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    def get_tourists_referred_nmb(self):
        all_tourists_referred = TouristProfile.objects.filter(user__generalprofile__referred_by=self.user)
        all_tourists_referred_nmb = all_tourists_referred.count()
        tourists_with_purchases_referred = Payment.objects.filter(order__tourist__in=all_tourists_referred)
        tourists_with_purchases_referred_nmb = tourists_with_purchases_referred.count()
        return {"total": all_tourists_referred_nmb, "with_purchases": tourists_with_purchases_referred_nmb}

    def get_guides_referred(self):
        all_guides_referred = TouristProfile.objects.filter(user__generalprofile__referred_by=self.user).count()
        guides_verified = GuideProfile.objects.filter(user__generalprofile__is_verified=True).count()
        return {"total": all_guides_referred, "verified": guides_verified}

    def get_referral_perks(self):
        if hasattr(self.user, "guideprofile") and self.user.generalprofile.is_fee_free:
            referral_perks = (('No service fee for five years (5 for 5 promo).'),)
        else:
            referral_perks = None
        return referral_perks

    def get_coupons(self):
        if self.user.couponuser_set.filter(redeemed_at__isnull=True).exists():
            coupon_user = self.user.couponuser_set.filter(redeemed_at__isnull=True)
            coupons = [item.coupon for item in coupon_user.iterator()]
        else:
            coupons = None
        return coupons

    def get_user_proficient_languages(self):
        return self.user.userlanguage_set.filter(level_id__in=[1, 2]).order_by("language")#native, advances - maybe to change their titles or add upper intermediate?

    def set_interests_from_list(self, interests_list):
        user = self.user
        user_interest_ids = list()
        for interest_name in interests_list:
            interest, created = Interest.objects.get_or_create(name=interest_name.lower())
            user_interest, created = UserInterest.objects.update_or_create(user=user, interest=interest, is_active=True)
            user_interest_ids.append(user_interest.id)
            print(user_interest_ids)
            print(user_interest.id)
        UserInterest.objects.filter(user=user).exclude(id__in=user_interest_ids).update(is_active=False)

    def set_languages_from_list(self, languages_list):
        user = self.user
        user_language_ids = list()
        for language in languages_list:
            language_name = language.name
            language_level_id = language.level
            user_language, created = UserLanguage.objects.update_or_create(language=language_name, user=user,
                                                                           level_id=language_level_id, is_active=True)
            user_language_ids.append(user_language.id)
        UserLanguage.objects.filter(user=user).exclude(id__in=user_language_ids).update(is_active=False)


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
