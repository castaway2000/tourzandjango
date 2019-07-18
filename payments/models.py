from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Currency
from django.utils.translation import ugettext as _
from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY,  BRAINTREE_PRIVATE_KEY, ILLEGAL_COUNTRIES, ON_PRODUCTION
from utils.general import uuid_creating
import braintree
if ON_PRODUCTION:
    braintree.Configuration.configure(braintree.Environment.Production,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )
else:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )


#created mapping between users and braintree customers
class PaymentCustomer(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None)
    uuid = models.CharField(max_length=64)#from braintree
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username

    def save(self, *args, **kwargs):
        if not self.pk:
            result = braintree.Customer.create({
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
            })
            self.uuid = result.customer.id
        super(PaymentCustomer, self).save(*args, **kwargs)


    def payment_method_create(self, payment_method_nonce, make_default=False):
        payment_customer = self
        result = braintree.PaymentMethod.create({
            "customer_id": payment_customer.uuid,
            "payment_method_nonce": payment_method_nonce,
            "options": {
                "verify_card": True,
                # "fail_on_duplicate_payment_method": True,
                # True #first payment method of a customer will be marked as "default"

                #just checkbox without being a part of a form returns "on" instead of True if it is checked
                "make_default": make_default
            }
        })

        # print(result)
        # print(result.payment_method.token)
        # print(result.payment_method.__class__.__name__)

        try:
            """
            AT 02092018: The case with adding of previously deleted payment method needs to be done with real cards.
            It works OK on the test environment.
            There is a chance the newly added payment method, which was deactivated before, will have another token
            and that is why it will be OK.
            """
            response_data = result.payment_method
            token = response_data.token
            kwargs = {
                "user": self.user,
                "token": token
            }

            #depending on payment method different set of fields should be added
            if result.payment_method.__class__.__name__ == 'CreditCard':
                kwargs["is_default"] = response_data.default
                last_4_digits = response_data.verifications[0]["credit_card"]["last_4"]
                card_number = "XXXX-XXXX-XXXX-%s" % last_4_digits
                kwargs["card_number"] = card_number
                card_type = response_data.verifications[0]["credit_card"]["card_type"]
                card_type, created = PaymentMethodType.objects.get_or_create(name=card_type)
                kwargs["type"] = card_type
                PaymentMethod.objects.create(**kwargs)

            elif result.payment_method.__class__.__name__ == 'PayPalAccount':#paypal
                print ("PayPal")
                kwargs["is_default"] = response_data.default
                kwargs["is_paypal"] = True
                kwargs["paypal_email"] = response_data.email
                type, created = PaymentMethodType.objects.get_or_create(name="paypal")
                kwargs["type"] = type
                PaymentMethod.objects.create(**kwargs)
            message = _('A new payment method was successfully added!')
            return {"status": "success", "message": message}
        except Exception as e:
            message = _('A new payment was not added! Details: %s. Response object: %s' % (e, result))
            return {"status": "error", "message": message}


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
    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
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
        if not self.uuid:
            self.uuid = uuid_creating()

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

        #automatically set the default payment method if current default is being deleted
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


    def set_as_default(self):
        payment_method = self
        # all other Payment methods on Braintree side will be automatically updated to make_default = False
        try:
            result = braintree.PaymentMethod.update(payment_method.token, {
                "options": {
                    "make_default": True,
                    "verify_card": False,
                }
            })
            # print(result)
            if result.is_success:
                payment_method.is_default = True
                payment_method.save()
                message = _('New default payment method has been applied successfully!')
                status =  "success"
            else:
                message = _('Failure during changing of the default payment method!')
                status ="error"
        except Exception as e:
            message = _('Failure during request for changing of the default payment method!')
            status = "error"
        return {"status": status, "message": message}

    def deactivate(self):
        payment_method = self
        try:
            result = braintree.PaymentMethod.delete(payment_method.token)
            if result.is_success:
                payment_method.is_default = False
                payment_method.is_active = False
                payment_method.save()
                message = _('Payment method has been deleted successfully!')
                status = "success"
            else:
                message = _('Failure during deleting of the payment method!')
                status = "error"
        except Exception as e:
            message = _('Failure during request for deleting of the payment method!')
            status = "error"
        return {"status": status, "message": message}


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