from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from guides.models import GuideProfile
from orders.models import Order, Review
from django.db.models.signals import post_save

from guides.models import GuideProfile
from utils.disabling_signals_for_load_data import disable_for_loaddata
from django.contrib.gis.geos import Point
import uuid
point = Point(1, 1)


class GeoTracker(models.Model):
    user = models.ForeignKey(User)
    is_online = models.IntegerField(default=0, null=False, blank=False)
    geo_point = models.PointField(geography=True, default=point, blank=False)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    trip_in_progress = models.BooleanField(default=False, null=False, blank=False)


class GeoTrip(models.Model):
    user = models.ForeignKey(User, related_name='geotrip_user')
    guide = models.ForeignKey(User, related_name='geotrip_guide')
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    duration = models.IntegerField()
    in_progress = models.BooleanField(default=False, null=False, blank=False)
    cost = models.FloatField()
    time_remaining = models.IntegerField()
    time_flag = models.CharField(max_length=64)
    order = models.OneToOneField(Order, blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        print('save() is called.')
        super(GeoTrip, self).save(*args, **kwargs)


class GeoChat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    guide = models.ForeignKey(User, related_name="guide_id")
    tourist = models.ForeignKey(User, related_name="tourist_id")
    topic_id = models.CharField(max_length=256, blank=True, null=True, default=None)#some topic can be specified as well
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s-%s" % (self.guide.generalprofile.first_name, self.tourist.generalprofile.first_name)


class GeoChatMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(GeoChat)
    message = models.TextField()
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s: %s" % (self.chat.created, self.user.username)


    def save(self, *args, **kwargs):
        super(GeoChatMessage, self).save(*args, **kwargs)

    def get_receiver_user(self):
        current_user = self.user
        chat = self.chat
        if current_user:
            receiver_user = chat.tourist if chat.tourist != current_user else chat.guide
        else:
            receiver_user = None
        return receiver_user


@disable_for_loaddata
def chat_message_post_save(sender, instance, created, **kwargs):
    receiver_user = instance.get_receiver_user()

    if receiver_user and not receiver_user.generalprofile.get_is_user_online():
        data = {"chat_message": instance, "user_from": instance.user, "user_to": receiver_user}
post_save.connect(chat_message_post_save, sender=GeoChatMessage)


