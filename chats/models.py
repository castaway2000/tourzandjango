from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour


class Chat(models.Model):
    guide = models.ForeignKey(User, related_name="guide")
    tourist = models.ForeignKey(User, related_name="tourist")
    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)#a chat converstion can be around some specific tour
    topic = models.CharField(max_length=256, blank=True, null=True, default=None)#some topic can be specified as well
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.id


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat)
    message = models.TextField()
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.user.username


