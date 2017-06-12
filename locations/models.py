from __future__ import unicode_literals

from django.db import models


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
    image = models.ImageField(upload_to="locations/cities", blank=True, null=True, default=None)
    is_featured = models.BooleanField(default=False)#for showing on Homepage
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


#cities, countries currencies are needed to be remade for using external packages later
class Currency(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


