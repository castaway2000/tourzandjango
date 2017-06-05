from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour
from django.utils.text import slugify
from guides.models import GuideProfile, Service
from tourists.models import TouristProfile
from django.db.models.signals import post_save
from django.db.models import Sum, Count, Avg
from crequest.middleware import CrequestMiddleware
from utils.sending_emails import SendingEmail


class OrderStatus(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=None, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
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

        #preventing creating of the order if guide and tourist is the same user
        # if not self.pk and self.guide.user == self.tourist.user:
        #     return False
        if self.hours_nmb and self.price_hourly:
            print (self.hours_nmb)
            print (self.price_hourly)
            self.price = int(self.hours_nmb) * float(self.price_hourly)

        #calculating tour price
        price_after_discount = self.price - self.discount
        self.price_after_discount = price_after_discount

        self.total_price = price_after_discount + self.additional_services_price

        data = {"order": self}
        a = SendingEmail(data)

        super(Order, self).save(*args, **kwargs)


"""
saving ratings from review to Order object
"""
def order_post_save(sender, instance, created, **kwargs):
    guide = instance.guide

    statistic_info = guide.order_set.filter(review__is_tourist_feedback=True)\
        .aggregate(rating=Avg("rating_guide"), reviews_nmb=Count("id"))
    print (statistic_info)

    if statistic_info["rating"] and statistic_info["reviews_nmb"]:
        guide.orders_with_review_nmb = statistic_info["reviews_nmb"]
        guide.rating = statistic_info["rating"]
        guide.save(force_update=True)

post_save.connect(order_post_save, sender=Order)


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

    def save(self, *args, **kwargs):
        self.price_after_discount = self.discount
        super(ServiceInOrder, self).save(*args, **kwargs)

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

    guide_feedback_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    guide_feedback_text = models.TextField(blank=True, null=True, default=None)
    guide_rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_guide_feedback = models.BooleanField(default=False)
    guide_review_created = models.DateTimeField(blank=True, null=True, default=None)
    guide_review_updated = models.DateTimeField(blank=True, null=True, default=None)

    tourist_feedback_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    tourist_feedback_text = models.TextField(blank=True, null=True, default=None)
    tourist_rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_tourist_feedback = models.BooleanField(default=False)
    tourist_review_created = models.DateTimeField(blank=True, null=True, default=None)
    tourist_review_updated = models.DateTimeField(blank=True, null=True, default=None)

    def __unicode__(self):
        if self.order:
            return "%s" % self.order.tour.name
        else:
            return "%s" % self.id


    def save(self, *args, **kwargs):
        super(Review, self).save(*args, **kwargs)


"""
saving ratings from review to Order object
"""
def review_post_save(sender, instance, created, **kwargs):
    order = instance.order
    order.rating_tourist = instance.guide_rating
    order.rating_guide = instance.tourist_rating
    order.save(force_update=True)

post_save.connect(review_post_save, sender=Review)
