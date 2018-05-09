from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Currency


#created mapping between users and braintree customers
class PaymentCustomer(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    uuid = models.CharField(max_length=64)#from braintree
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username


class PaymentMethodType(models.Model):
    name = models.CharField(max_length=32)
    logo = models.ImageField(upload_to="cards/", blank=True, null=True, default="cards/mastercard-curved-32px.png")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    card_number = models.CharField(max_length=32, null=True, blank=True)
    type = models.ForeignKey(PaymentMethodType, blank=True, null=True, default=None)
    token = models.CharField(max_length=32)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_paypal = models.BooleanField(default=False)
    paypal_email = models.EmailField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "%s %s" % (self.user.username, self.name)
        else:
            return "%s" % self.user.username

    def __init__(self, *args, **kwargs):
        super(PaymentMethod, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):

        #if default is set to a curent payment method, all other payment methods are being updated to default=False
        if (not self.pk and self.is_default==True) \
                or (self.is_default != self._original_fields["is_default"] and self.is_default == True):
            PaymentMethod.objects.filter(user=self.user, is_default=True, is_active=True).update(is_default=False)

        #this logic is on view but this code is needed for API is well
        #set a first added method as a default one
        if not self.pk and self.is_default==False:
            other_payment_methods = PaymentMethod.objects.filter(user=self.user, is_active=True).exists()
            if not other_payment_methods:
                self.is_default = True

        #aset utomatically set the default payment method if current default is being deleted
        if self.pk and self.is_active != self._original_fields["is_active"] and self.is_active == False:
            other_payment_methods_default = PaymentMethod.objects.filter(user=self.user, is_active=True, is_default=True)\
                .exclude(id=self.id)
            if not other_payment_methods_default:
                other_payment_methods = PaymentMethod.objects.filter(user=self.user, is_active=True).exclude(id=self.id)
                if other_payment_methods:
                    last_payment_method = other_payment_methods.last()
                    #not to trigger save method
                    PaymentMethod.objects.filter(id=last_payment_method.id).update(is_default=True)

        super(PaymentMethod, self).save(*args, **kwargs)


class Payment(models.Model):
    order = models.ForeignKey('orders.Order', blank=True, null=True, default=None)#maybe it can be a payment without an order
    payment_method = models.ForeignKey(PaymentMethod)
    uuid = models.CharField(max_length=36, blank=True, null=True, default=None)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None)
    dt_paid = models.DateTimeField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id