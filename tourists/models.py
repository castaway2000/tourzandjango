from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


#tourist profile which is created by default for all users
class TouristProfile(models.Model):
    user = models.OneToOneField(User)
    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to="users/images", blank=True, null=True, default=None)
    about = models.TextField(max_length=5000, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username


class TouristTravelPhoto(models.Model):
    user = models.ForeignKey(User)
    image = models.ImageField(upload_to="tourist/travel_photos")
    order = models.ForeignKey("orders.Order", blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username


