from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.general import random_string_creating
from django.utils.text import slugify
from datetime import date



class Interest(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


class UserInterest(models.Model):
    user = models.ForeignKey(User)
    interest = models.ForeignKey(Interest)

    def __unicode__(self):
        if self.interest.name:
            return "%s" % self.interest.name
        else:
            return "%s" % self.interest.id


#tourist profile which is created by default for all users
class Profile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="users/images", blank=True, null=True, default=None)
    about = models.TextField(max_length=5000, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username


class GuideProfile(models.Model):
    user = models.OneToOneField(User)
    city = models.ForeignKey(City)

    name = models.CharField(max_length=256, blank=True, null=True, default=None)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    overview = models.TextField(blank=True, null=True, default=None)
    date_of_birth = models.DateField(blank=True, null=True, default=None)
    age = models.IntegerField(default=0)

    header_image = models.ImageField(upload_to="guides/header_images", blank=True, null=True, default="guides/header_images/300x300.png")
    profile_image = models.ImageField(upload_to="guides/profile_images", blank=True, null=True, default="guides/profile_images/300x300.png")
    optional_image = models.ImageField(upload_to="guides/optional_images", blank=True, null=True, default="guides/optional_images/300x300.png")
    slug = models.SlugField(max_length=200, unique=True, default=random_string_creating)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username

    #add logic to perform calculations only if the value was changed
    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)

        if self.date_of_birth:
            today = date.today()
            date_of_birth = self.date_of_birth
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            self.age = age
        super(GuideProfile, self).save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=256)
    html_field_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        name_slashed = self.name.replace(" ", "_").lower()
        self.html_field_name = "is_%s" % name_slashed
        super(Service, self).save(*args, **kwargs)


class GuideService(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    guide = models.ForeignKey(GuideProfile)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.service.name
