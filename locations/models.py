from __future__ import unicode_literals

from django.db import models
from utils.uploadings import upload_path_handler_city
from django.utils.text import slugify
from utils.images_resizing import optimize_size
from utils.general import random_string_creating


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


class City(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    image = models.ImageField(upload_to=upload_path_handler_city, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_city, blank=True, null=True, default=None)
    is_featured = models.BooleanField(default=False)#for showing on Homepage
    is_active = models.BooleanField(default=True)
    place_id = models.CharField(max_length=128, blank=True, null=True)
    original_name = models.CharField(max_length=128, blank=True, null=True)
    full_location = models.CharField(max_length=256, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating)
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

        if self._original_fields["image"] != self.image:
            self.image = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")

        super(City, self).save(*args, **kwargs)



#cities, countries currencies are needed to be remade for using external packages later
class Currency(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


