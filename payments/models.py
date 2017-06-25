from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Currency



class PaymentCustomer(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    uuid = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username


class CardType(models.Model):
    name = models.CharField(max_length=32)
    logo = models.ImageField(upload_to="cards/", blank=True, null=True, default="cards/mastercard-curved-32px.png")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    name = models.CharField(max_length=64)
    card_number = models.CharField(max_length=32)
    card_type = models.ForeignKey(CardType, blank=True, null=True, default=None)
    token = models.CharField(max_length=32)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "%s %s" % (self.user.username, self.name)
        else:
            return "%s" % self.user.username


class Payment(models.Model):
    order = models.OneToOneField('orders.Order', blank=True, null=True, default=None)#maybe it can be a payment without an order
    payment_method = models.ForeignKey(PaymentMethod)
    uuid = models.CharField(max_length=36, blank=True, null=True, default=None)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None)
    date_paid = models.DateField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id