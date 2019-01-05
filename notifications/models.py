from django.db import models
from orders.models import Order
from django.contrib.auth.models import User


class Banner(models.Model):
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=240)
    url = models.URLField(default=None, null=True)
    call_to_action = models.CharField(max_length=32, default='')
    active = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.title


class NotificationSubject(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class Notification(models.Model):
    subject = models.ForeignKey(NotificationSubject, blank=True, null=True, default=None)
    order = models.ForeignKey(Order, blank=True, null=True, default=None)
    # to track case for not sending sms to often when chat is not related to order
    chat = models.ForeignKey("chats.Chat", blank=True, null=True, default=None)
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    phone = models.CharField(max_length=64, blank=True, null=True, default=None)
    email = models.EmailField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    is_tourist = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.phone

    def save(self, *args, **kwargs):
        if self.order and self.user == self.order.tourist:
            self.is_tourist = True
        super(Notification, self).save(*args, **kwargs)