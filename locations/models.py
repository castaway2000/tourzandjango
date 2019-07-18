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
import time
from django.core.files.uploadedfile import SimpleUploadedFile
from utils.unsplash import get_image
from utils.wikitravel import get_location_summary
from django.contrib.auth.models import User
from utils.sending_emails import SendingEmail
from django.db.models.signals import post_save
from utils.disabling_signals_for_load_data import disable_for_loaddata


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
    meta_title = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
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

        if not self.description:
            self.description = get_location_summary(self.name)

        if not self.image:
            #But so far we get a default image from unsplash here
            search_term = self.name
            content, file_name = get_image(search_term=search_term, image_name=self.slug)
            if file_name:
                self.image = SimpleUploadedFile(file_name, content)

        if self.image:
            if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
                self.image_large = optimize_size(self.image, "large")
                self.image_medium = optimize_size(self.image, "medium")
                self.image_small = optimize_size(self.image, "small")
        else:
            pass
            #maybe to put here a code to remove related sized images, if a main image is removed

        super(Country, self).save(*args, **kwargs)

    def get_cities(self):
        cities = self.city_set.filter(is_active=True).order_by("name")
        return cities

    def get_blog_posts(self):
        return self.blogpost_set.filter(is_active=True)

    def get_absolute_url(self):
        # return reverse('guides', kwargs={'name': self.name, 'uuid': self.uuid, 'overview': 'overview'})
        return '/guides/in/{}/'.format(self.name).replace(' ', '%20').lower()

    def get_country_tourism_url(self):
        return '/{}-tourism/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_visit_country_url(self):
        return '/visit-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_country_travel_guide_url(self):
        return '/{}-travel-guide/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_country_guided_tours_url(self):
        return '/{}-guided-tours/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_guided_tours_of_country_url(self):
        return '/guided-tours-of-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_private_tours_of_country_url(self):
        return '/private-tours-of-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_country_tours_url(self):
        return '/{}-tours/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()



class City(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating)
    country = models.ForeignKey(Country, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
    meta_title = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
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

        if not self.description or self.description == 'None':
            self.description = get_location_summary(self.name, self.full_location)

        if not self.image:
            #But so far we get a default image from unsplash here
            search_term = "%s cityscape" % self.name
            content, file_name = get_image(search_term=search_term, image_name=self.slug)
            if file_name:
                self.image = SimpleUploadedFile(file_name, content)

        if self.image:
            if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
                self.image_large = optimize_size(self.image, "large")
                self.image_medium = optimize_size(self.image, "medium")
                self.image_small = optimize_size(self.image, "small")
        else:
            pass

        if not self.country or (self._original_fields["place_id"] != self.place_id) or (self.place_id and not self.country and not self._original_fields["country"]):
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

    def get_tours(self, nmb=100):
        tours = self.tour_set.filter(is_active=True).order_by("name")[:nmb]
        return tours

    def get_guides(self, nmb=100):
        guides = self.guideprofile_set.filter(is_active=True)[:nmb]
        return guides

    def get_tours_12(self):
        tours = self.get_tours(12)
        return tours

    def get_guides_12(self):
        guides = self.get_guides(12)
        return guides

    def get_tours_6(self):
        tours = self.get_tours(6)
        return tours

    def get_guides_6(self):
        guides = self.get_guides(6)
        return guides

    def get_special_offer_tours(self):
        special_offers_items = self.tour_set.filter(is_active=True)
        special_offer_tours = list()
        count = 0
        for special_offers_item in special_offers_items:
            dtour = special_offers_item.available_discount_tours()
            if len(dtour) > 0:
                special_offer_tours.append(special_offers_item)
                if count == 4:
                    break
                count += 1
        return special_offer_tours

    def get_average_guide_rate(self):
        data = self.guideprofile_set.filter(is_active=True).aggregate(Avg('rate'))
        avg = data.get("rate__avg")
        if avg:
            return "%.2f" % float(avg)
        else:
            return None

    def get_average_tour_price(self):
        data = self.tour_set.filter(is_active=True, type="1").aggregate(Avg('price'))
        avg = data.get("price__avg")
        if avg:
            return "%.2f" % float(avg)
        else:
            return None

    def get_blog_posts(self):
        return self.blogpost_set.filter(is_active=True)

    def get_absolute_url(self):
        # return reverse('guides', kwargs={'name': self.name, 'uuid': self.uuid, 'overview': 'overview'})
        return '/guides/in/{}/{}/'.format(self.country, self.name).lower().replace(' - ', '-').replace(', ', '-').replace(' ', '-')

    def get_city_tourism_url(self):
        return '/{}-tourism/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_visit_city_url(self):
        return '/visit-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_city_travel_guide_url(self):
        return '/{}-travel-guide/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_city_guided_tours_url(self):
        return '/{}-guided-tours/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_guided_tours_of_city_url(self):
        return '/guided-tours-of-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_private_tours_of_city_url(self):
        return '/private-tours-of-{}/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()

    def get_city_tours_url(self):
        return '/{}-tours/'.format(self.name).replace(' - ', '-').replace(', ', '-').replace(' ', '-').lower()


#cities, countries currencies are needed to be remade for using external packages later
class Currency(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class SearchLog(models.Model):
    session_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    country = models.ForeignKey(Country, blank=True, null=True, default=None)
    city = models.ForeignKey(City, blank=True, null=True, default=None)
    search_term = models.CharField(max_length=64, blank=True, null=True, default=None)
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        if self.search_term:
            return "%s" % self.search_term
        elif self.country:
            return "%s" % self.country.name
        elif self.city:
            return "%s" % self.city.name
        else:
            return "%s" % self.id

    def create(self, request, city, country, search_term):
        kwargs = dict()
        kwargs["session_id"] = request.session.session_key
        if not request.user.is_anonymous():
            kwargs["user"] = request.user
        if city:
            kwargs["city"] = city
        elif country:
            kwargs["country"] = country
        elif search_term:
            kwargs["search_term"] = search_term
        SearchLog.objects.create(**kwargs)
        return True


class NewLocationTourRequest(models.Model):
    NEW = "10"
    PROCESSING = "20"
    PROCESSED = "30"
    CANCELLED = "40"
    STATUSES = (
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (PROCESSED, "Processed"),
        (CANCELLED, "Cancelled"),
    )
    location_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    location_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    first_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    email = models.EmailField(blank=True, null=True, default=None)
    description = models.TextField(max_length=3000, blank=True, null=True, default=None)
    tour_date = models.DateTimeField(blank=True, null=True, default=None)
    number_persons = models.IntegerField(default=1)
    status = models.CharField(choices=STATUSES, max_length=20, default=NEW)
    tourzan_notes = models.TextField(max_length=3000, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Id %s: %s" % (self.id, self.status)


@disable_for_loaddata
def new_location_request_post_save(sender, instance, created, **kwargs):
    SendingEmail({}).email_booking_in_new_location_request()
post_save.connect(new_location_request_post_save, sender=NewLocationTourRequest)

