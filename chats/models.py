from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour

import uuid


class Chat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    guide = models.ForeignKey(User, related_name="guide")
    tourist = models.ForeignKey(User, related_name="tourist")
    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)#a chat converstion can be around some specific tour
    topic = models.CharField(max_length=256, blank=True, null=True, default=None)#some topic can be specified as well
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s-%s" % (self.guide.guideprofile.name, self.tourist.username)


class ChatMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat)
    message = models.TextField()
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s: %s" % (self.chat.created, self.user.username)


