from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City


class Profile(models.Model):
    user = models.ForeignKey(User)
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

    header_image = models.ImageField(upload_to="guides/header_image", blank=True, null=True, default=None)
    profile_image = models.ImageField(upload_to="guides/header_image", blank=True, null=True, default=None)
    optional_image = models.ImageField(upload_to="guides/header_image", blank=True, null=True, default=None)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username