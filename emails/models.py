from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class EmailMessageType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


class EmailMessage(models.Model):
    type = models.ForeignKey(EmailMessageType)
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    order = models.ForeignKey("orders.Order", blank=True, null=True, default=None)
    chat_message = models.ForeignKey("chats.ChatMessage", blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.email