from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sitemaps import ping_google

from utils.general import random_string_creating, uuid_creating
from django.utils.text import slugify
from datetime import date
from django.contrib.auth.models import User
from locations.models import City, Currency
from utils.uploadings import (upload_path_handler_guide_header_images,
                              upload_path_handler_guide_profile_image,
                              upload_path_handler_guide_profile_image_large,
                              upload_path_handler_guide_profile_image_medium,
                              upload_path_handler_guide_profile_image_small,
                              upload_path_handler_guide_optional_image,
                              upload_path_handler_guide_answer_image,
                              upload_path_handler_guide_answer_image_large,
                              upload_path_handler_guide_answer_image_medium,
                              upload_path_handler_guide_answer_image_small,
                              upload_path_handler_guide_license
                              )
from django.core.validators import FileExtensionValidator
from utils.images_resizing import optimize_size
from django.utils.translation import ugettext as _


class GuideProfile(models.Model):
    user = models.OneToOneField(User)
    city = models.ForeignKey(City)

    name = models.CharField(max_length=256, blank=True, null=True, default=None)

    rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=1)
    min_hours = models.IntegerField(default=1)
    additional_person_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    is_default_guide = models.BooleanField(default=True)
    overview = models.TextField(blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=0)

    #not used. DELETE THEM?
    header_image = models.ImageField(upload_to=upload_path_handler_guide_header_images, blank=True, null=True, default=None)
    optional_image = models.ImageField(upload_to=upload_path_handler_guide_optional_image, blank=True, null=True, default=None)


    profile_image = models.ImageField(upload_to=upload_path_handler_guide_profile_image, blank=True, null=True, default=None,
                                      validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    profile_image_large = models.ImageField(upload_to=upload_path_handler_guide_profile_image_large, blank=True, null=True, default=None)
    profile_image_medium = models.ImageField(upload_to=upload_path_handler_guide_profile_image_medium, blank=True, null=True, default=None)
    profile_image_small = models.ImageField(upload_to=upload_path_handler_guide_profile_image_small, blank=True, null=True, default=None)

    license_image = models.ImageField(upload_to=upload_path_handler_guide_license, blank=True, null=True, default="guides/optional_images/300x300.png")
    slug = models.SlugField(max_length=200, unique=True, default=random_string_creating)
    uuid = models.CharField(max_length=48, blank=True, null=True)
    is_use_calendar = models.BooleanField(default=False)

    #statistic data
    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    orders_nmb = models.IntegerField(default=0)
    orders_completed_nmb = models.IntegerField(default=0)
    orders_with_review_nmb = models.IntegerField(default=0)
    orders_with_review_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)# from total orders_completed_nmb
    orders_reviewed_nmb = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username

    def __init__(self, *args, **kwargs):
        super(GuideProfile, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    #add logic to perform calculations only if the value was changed
    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)

        if self.date_of_birth:
            today = date.today()
            date_of_birth = self.date_of_birth
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            self.age = age

        try:
            self.orders_with_review_rate = (self.orders_with_review_nmb/self.orders_completed_nmb)*100
        except Exception as e:
            print (e)

        if not self.uuid:
            self.uuid = uuid_creating()

        if not self.pk and self.user.generalprofile.referred_by:
            self.add_statistics_for_referrer()


        if self._original_fields["profile_image"] != self.profile_image or (self.profile_image and (not self.profile_image_large or not self.profile_image_medium or not self.profile_image_small)):
            self.profile_image_small = optimize_size(self.profile_image, "small")
            self.profile_image_medium = optimize_size(self.profile_image, "medium")
            self.profile_image_large = optimize_size(self.profile_image, "large")

        super(GuideProfile, self).save(*args, **kwargs)

        try:
            ping_google()
        except Exception:
            pass

    def get_hours_nmb_range(self):
        min_hours_nmb = self.min_hours

        min_hours_nmb_range_basic = range(min_hours_nmb, min_hours_nmb+5)
        min_hours_nmb_range_full = range(min_hours_nmb, min_hours_nmb+10)

        return {"min_hours_nmb_range_basic": min_hours_nmb_range_basic,
                "min_hours_nmb_range_full": min_hours_nmb_range_full}

    def get_absolute_url(self):
        # return reverse('guides', kwargs={'name': self.name, 'uuid': self.uuid, 'overview': 'overview'})
        return '/guides/{}/{}/overview/'.format(self.name, self.user.generalprofile.uuid).replace(' ', '%20')

    def add_statistics_for_referrer(self):
        referred_by = self.user.generalprofile.referred_by
        if referred_by:
            referred_by.generalprofile.guides_referred_nmb += 1
            referred_by.generalprofile.save(force_update=True)

    def get_tours(self):
        return self.tour_set.filter(is_active=True, is_deleted=False)

    @property
    def guide_rate(self):
        if self.rate > 0:
            return "%s %s/%s" % (self.rate, self.currency.name, _("hour"))
        else:
            return _("free tours!")

    @property
    def first_name(self):
        if self.user and self.user.generalprofile:
            return self.user.generalprofile.first_name
        else:
            return None


class Service(models.Model):
    name = models.CharField(max_length=256)
    html_field_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        name_slashed = self.name.replace(" ", "_").lower()
        self.html_field_name = "is_%s" % name_slashed
        super(Service, self).save(*args, **kwargs)


class GuideService(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    guide = models.ForeignKey(GuideProfile)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.service.name


class Question(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.text

    def get_text_with_city(self, guide):
        if "{city}" in self.text:
            if guide.city and guide.city.name:
                return self.text.format(city=guide.city.name)
            else:
                return self.text.format(city="your city")
        else:
            return self.text


class GuideAnswer(models.Model):
    guide = models.ForeignKey(GuideProfile)
    question = models.ForeignKey(Question)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_path_handler_guide_answer_image, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_guide_answer_image_large, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_guide_answer_image_medium, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_guide_answer_image_small, blank=True, null=True, default=None)

    order_priority = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % self.guide.user.generalprofile.first_name

    def __init__(self, *args, **kwargs):
        super(GuideAnswer, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
            try:
                self.image_small = optimize_size(self.image, "small")
                self.image_medium = optimize_size(self.image, "medium")
                self.image_large = optimize_size(self.image, "large")
            except:
                pass
        if not self.text or self.text == "":
            self.is_active = False
        else:
            self.is_active = True
        super(GuideAnswer, self).save(*args, **kwargs)

    def get_question_text_with_city(self):
        return self.question.get_text_with_city(self.guide)
