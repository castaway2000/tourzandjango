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
import time
from django.db.models import Avg


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
    description = models.TextField(blank=True, null=True)
    position_index = models.IntegerField(default=0)
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
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")
        super(Country, self).save(*args, **kwargs)

    def get_cities(self):
        cities = self.city_set.filter(is_active=True).order_by("name")
        return cities


class City(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating)
    country = models.ForeignKey(Country, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
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
        if not self.name:
            self.name = self.original_name
        self.slug = slugify(self.name)
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")

        if not self.country or (self._original_fields["place_id"] != self.place_id) or (self.place_id and not self.country and not self._original_fields["country"]):
            print("updating country")
            time.sleep(3)
            google_maps_key = GOOGLE_MAPS_KEY
            url_place_info = "https://maps.googleapis.com/maps/api/geocode/json?place_id=%s&key=%s" % (self.place_id, google_maps_key)
            r = requests.get(url_place_info)
            data = r.json()
            if data.get("status") == "OK":
                address_components = data["results"][0]["address_components"]
                if self.pk and not self.full_location:
                    self.full_location = data["results"][0].get("formatted_address")
                country_name = None
                for item in address_components:
                    if item.get("types"):
                        if "country" in item.get("types"):
                            country_name = item.get("long_name")
                        if self.pk and not self.original_name:
                            if "locality" in item.get("types"):
                                self.original_name = item.get("short_name")
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

    def get_tours_12(self):
        tours = self.tour_set.filter(is_active=True).order_by("name")[:12]
        return tours

    def get_guides_12(self):
        guides = self.guideprofile_set.filter(is_active=True)[:12]
        return guides

    def get_special_offer_tours(self):
        special_offers_items = self.tour_set.filter(is_active=True)
        special_offer_tours = list()
        count = 0
        for special_offers_item in special_offers_items:
            if len(special_offers_item.available_discount_tours) > 0:
                special_offer_tours.append(special_offers_item)
                if count == 4:
                    break
                count += 1
        return special_offer_tours

    def get_average_guide_rate(self):
        data = self.guideprofile_set.filter(is_active=True).aggregate(Avg('rate'))
        avg = data.get("rate__avg")
        if avg:
            return float(avg)
        else:
            return None

    def get_average_tour_price(self):
        data = self.tour_set.filter(is_active=True, type="1").aggregate(Avg('price'))
        avg = data.get("price__avg")
        if avg:
            return float(avg)
        else:
            return None


#cities, countries currencies are needed to be remade for using external packages later
class Currency(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


