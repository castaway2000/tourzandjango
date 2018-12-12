from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# from users.models import GeneralProfile
# from guides.models import GuideProfile
# from tourists.models import TouristProfile
# from orders.models import Order
# from chats.models import Chat, ChatMessage


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

#
# class DripMailer(models.Model):
#     user = models.ForeignKey(GeneralProfile, blank=True, null=True, default=None)
#     order = models.ForeignKey(Order, blank=True, null=True, default=None)
#     guide = models.ForeignKey(GuideProfile, blank=True, null=True, default=None)
#     tourist = models.ForeignKey(TouristProfile, blank=True, null=True, default=None)
#     chat = models.ForeignKey(Chat, blank=True, null=True, default=None)
#     chat_message = models.ForeignKey(ChatMessage, blank=True, null=True, default=None)
#     drip_type = models.ForeignKey(DripType, blank=True, null=True, default=None)
#     times_contacted = models.IntegerField(blank=True, null=True, default=0)
#     first_contact_datetime = models.DateTimeField(blank=True, null=True, default=None)
#     next_contact_datetime = models.DateTimeField(blank=True, null=True, default=None)
#     status = models.BooleanField(blank=True, null=True, default=False)
#     abort = models.BooleanField(blank=True, null=True, default=False)
#
#
# class DripType(models.Model):
#     type = models.CharField(blank=True, null=True, default=None)
#     max_contact_times = models.IntegerField(blank=True, null=True, default=0)
