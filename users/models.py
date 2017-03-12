from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.general import random_string_creating
from django.utils.text import slugify


class Profile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="users/images", blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username


class GuideProfile(models.Model):
    user = models.OneToOneField(User)
    city = models.ForeignKey(City)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    interests = models.TextField(blank=True, null=True, default=None)
    overview = models.TextField(blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=0)

    header_image = models.ImageField(upload_to="guides/header_images", blank=True, null=True, default=None)
    profile_image = models.ImageField(upload_to="guides/profile_images", blank=True, null=True, default=None)
    optional_image = models.ImageField(upload_to="guides/optional_images", blank=True, null=True, default=None)
    slug = models.SlugField(max_length=200, unique=True, default=random_string_creating)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(GuideProfile, self).save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


class ServiceGuide(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    guide = models.ForeignKey(GuideProfile)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.service.name
