from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour
from django.utils.text import slugify
from guides.models import GuideProfile
from tourists.models import TouristProfile


class OrderStatus(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=None, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.user.username)
        super(OrderStatus, self).save(*args, **kwargs)


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, blank=True, null=True, default=1)

    guide = models.ForeignKey(GuideProfile, blank=True, null=True, default=None)
    tourist = models.ForeignKey(TouristProfile, blank=True, null=True, default=None)

    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours_nmb = models.IntegerField(default=0)#if an hourly tour was specified
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    rating_tourist = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating_guide = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    comment = models.TextField(blank=True, null=True, default=None)
    date_ordered = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_paid = models.DateField(blank=True, null=True, default=None)
    date_booked_for = models.DateTimeField(blank=True, null=True, default=None)
    date_toured = models.DateField(blank=True, null=True, default=None)

    def __unicode__(self):
        if self.guide:
            return "%s" % (self.guide.user.username)
        else:
            return "%s" % (self.id)


class Payment(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None)#maybe it can be a payment without an order
    payment_system_id = models.CharField(max_length=128, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


class Review(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None)

    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    text = models.TextField(blank=True, null=True, default=None)
    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    is_from_tourist = models.BooleanField(default=False)
    is_from_guide = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        if self.order:
            return "%s" % self.order.tour.name
        else:
            return "%s" % self.id