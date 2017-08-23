from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.uploadings import *
from django.utils.text import slugify
from utils.general import random_string_creating
from guides.models import GuideProfile
from utils.images_resizing import optimize_size


class PaymentType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class Tour(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    overview = models.TextField(blank=True, null=True, default=None)
    image = models.ImageField(upload_to=upload_path_handler_tour, blank=True, null=True, default="/tours/images/default_tour_image.jpg")
    image_medium = models.ImageField(upload_to=upload_path_handler_tour_medium, blank=True, null=True, default="/tours/images/default_tour_image_medium.jpg")
    image_small = models.ImageField(upload_to=upload_path_handler_tour_small, blank=True, null=True, default="/tours/images/default_tour_image_small.jpg")


    guide = models.ForeignKey(GuideProfile)
    city = models.ForeignKey(City, blank=True, null=True, default=None)

    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    #for fixed price tours
    currency = models.ForeignKey(Currency, blank=True, null=True, default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours = models.IntegerField(default=0)

    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    min_hours = models.IntegerField(default=0)

    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)#in decimals

    payment_type = models.ForeignKey(PaymentType, blank=True, null=True, default=None)#hourly or fixed price
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, default=random_string_creating)

    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Tour, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def __str__(self):
        if self.name:
            return "%s %s" % (self.id, self.name)
        else:
            return "%s" % self.id

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if self.payment_type_id == 1: #hourly

            self.price = 0
            self.hours = 0
            self.is_free = False

        if self.payment_type_id == 2: #paid

            self.price_hourly = 0
            self.min_hours = 0
            self.is_free = False

        if self.payment_type_id == 3: #free
            self.is_free = True

            self.price = 0
            self.hours = 0
            self.price_hourly = 0
            self.min_hours = 0


        if self._original_fields["image"] != self.image or (self.image and (not self.image_medium or not self.image_small)):
            self.image_small = optimize_size(self.image, "small")
            self.image_medium = optimize_size(self.image, "medium")

        super(Tour, self).save(*args, **kwargs)

    def get_hours_nmb_range(self):
        min_hours_nmb = self.min_hours

        min_hours_nmb_range_basic = range(min_hours_nmb, min_hours_nmb+5)
        min_hours_nmb_range_full = range(min_hours_nmb, min_hours_nmb+10)

        return {"min_hours_nmb_range_basic": min_hours_nmb_range_basic,
                "min_hours_nmb_range_full": min_hours_nmb_range_full}

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, blank=True, null=True)
    image = models.ImageField(upload_to=upload_path_handler_tour_images)
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.tour.name

    """
    reading of initial values for fields to compare them with values on save if needed
    """
    def __init__(self, *args, **kwargs):
        super(TourImage, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):

        if not self.pk:
            print("self.pk")
            print(self.tour.image.url)

            if self.tour.image.url.endswith("default_tour_image.jpg"):
                self.tour.image = self.image
                self.tour.save(force_update=True)

                self.is_main = True
        else:
            """
            setting an image on tour instance if it is set here
            """
            for field in self._meta.local_fields:
                if field.name == "is_main" and self.tour:
                    old = self._original_fields[field.name]
                    new = getattr(self, field.name)
                    if old != new and new == True:#if new value is True

                        #put is_main flag to False to other possible existing images
                        self.tour.tourimage_set.filter(is_main=True).update(is_main=False)
                        self.tour.image = self.image
                        self.tour.save(force_update=True)

        super(TourImage, self).save(*args, **kwargs)
