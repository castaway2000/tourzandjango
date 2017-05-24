from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour
from django.utils.text import slugify
from guides.models import GuideProfile, Service
from tourists.models import TouristProfile
from django.db.models.signals import post_save
from django.db.models import Sum


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

    tour = models.ForeignKey(Tour, blank=True, null=True, default=False)

    #if a guide is booked directly or hourly tour was booked, here goes hourly price and final nmb of hours
    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours_nmb = models.IntegerField(default=0)#if an hourly tour was specified

    #if a fixed-price tour is ordered, its price goes here
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    additional_services_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

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


    def save(self, *args, **kwargs):

        #calculating tour price
        price_after_discount = self.price - self.discount
        self.price_after_discount = price_after_discount

        self.total_price = price_after_discount + self.additional_services_price
        super(Order, self).save(*args, **kwargs)



class ServiceInOrder(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=False)
    service = models.ForeignKey(Service)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        if self.guide:
            return "%s" % (self.service.name)
        else:
            return "%s" % (self.id)


"""
saving sum of all additional services to order
"""
def service_in_order_post_save(sender, instance, created, **kwargs):
    order = instance
    additional_services = order.serviceinorder_set.filter(is_active=True)\
        .aggregate(total_price = Sum('price_after_discount'))

    additional_services_total_price = additional_services.get("total_price", 0)
    order.additional_services_price = additional_services_total_price
    order.save(force_update=True)

post_save.connect(service_in_order_post_save, sender=ServiceInOrder)


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