from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour


class OrderStatus(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.name


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, blank=True, null=True, default=None)
    user = models.ForeignKey(User)#who creates an order

    #tour can be defined hourly tour is a default one for every guide
    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)#has an user on it, who created a tour
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=8, decimal_places=2)
    hours_nmb = models.ImageField(default=0)#if an hourly tour was specified

    comment = models.TextField(blank=True, null=True, default=None)
    date_ordered = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_toured = models.DateField(blank=True, null=True, default=None)
    date_paid = models.DateField(blank=True, null=True, default=None)

    def __unicode__(self):
        return "%s" % (self.user.username)


class Payment(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None)#maybe it can be a payment without an order
    payment_system_id = models.CharField(max_length=128, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.name