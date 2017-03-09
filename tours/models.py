from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City


class PaymentType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name


class Tour(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    image = models.ImageField(upload_to="tours/images", blank=True, null=True, default=None)

    user = models.ForeignKey(User)
    city = models.ForeignKey(City, blank=True, null=True, default=None)
    currency = models.ForeignKey(Currency)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours = models.IntegerField(default=0)

    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    min_hours = models.IntegerField(default=0)

    payment_type = models.ForeignKey(PaymentType, blank=True, null=True, default=None)#hourly or fixed price
    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):

        if self.price_hourly > 0:
            self.payment_type_id = 1 #hourly
        elif self.price > 0:
            self.payment_type_id = 2 #paid
        elif self.is_free:
            self.payment_type_id = 3 #free

        super(Tour, self).save(*args, **kwargs)


class Review(models.Model):
    user = models.ForeignKey(User)
    tour = models.ForeignKey(Tour)
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.tour.name