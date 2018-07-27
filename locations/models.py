from __future__ import unicode_literals

from django.db import models
from utils.uploadings import (upload_path_handler_city, upload_path_handler_city_large,
                                upload_path_handler_city_medium, upload_path_handler_city_small,
                                upload_path_handler_country, upload_path_handler_country_large,
                                upload_path_handler_country_medium, upload_path_handler_country_small,)
from django.utils.text import slugify
from utils.images_resizing import optimize_size
from utils.general import random_string_creating
from tourzan.settings import GOOGLE_MAPS_KEY
import requests


class LocationType(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Location(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    full_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    type = models.ForeignKey(LocationType, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id


class Country(models.Model):
    #initial value is in English, all the translations for other languages can be done via django translation file
    name = models.CharField(max_length=256)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating)
    place_id = models.CharField(max_length=128)
    is_featured = models.BooleanField(default=False)#for showing on Homepage
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_path_handler_country, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_country_large, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_country_medium, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_country_small, blank=True, null=True, default=None)

    def __str__(self):
        return "%s" % self.name

    def __init__(self, *args, **kwargs):
        super(Country, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or self.image_medium or self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")
        super(Country, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating)
    country = models.ForeignKey(Country, blank=True, null=True, default=None)
    image = models.ImageField(upload_to=upload_path_handler_city, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_city_large, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_city_medium, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_city_small, blank=True, null=True, default=None)
    is_featured = models.BooleanField(default=False)#for showing on Homepage
    is_active = models.BooleanField(default=True)
    place_id = models.CharField(max_length=128, blank=True, null=True)
    original_name = models.CharField(max_length=128, blank=True, null=True)
    full_location = models.CharField(max_length=256, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    def __init__(self, *args, **kwargs):
        super(City, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or self.image_medium or self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")

        if (self._original_fields["place_id"] != self.place_id) or (self.place_id and not self.country and not self._original_fields["country"]):
            google_maps_key = GOOGLE_MAPS_KEY
            url_place_info = "https://maps.googleapis.com/maps/api/geocode/json?place_id=%s&key=%s" % (self.place_id, google_maps_key)
            r = requests.get(url_place_info)
            data = r.json()
            if data.get("status") == "OK":
                address_components = data["results"][0]["address_components"]
                country_name = None
                for item in address_components:
                    if item.get("types") and "country" in item.get("types"):
                        country_name = item.get("long_name")
                        break
                if country_name:
                    url_country_info = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (country_name, google_maps_key)
                    r = requests.get(url_country_info)
                    data = r.json()
                    if data.get("status") == "OK":
                        if "place_id" in data["results"][0]:
                            place_id = data["results"][0]["place_id"]
                            country, created = Country.objects.get_or_create(name=country_name, place_id=place_id)
                            self.country = country

        super(City, self).save(*args, **kwargs)



#cities, countries currencies are needed to be remade for using external packages later
class Currency(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


