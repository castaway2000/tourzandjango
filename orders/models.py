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
from locations.models import Currency
from utils.disabling_signals_for_load_data import disable_for_loaddata
from payments.models import Payment, PaymentMethod
from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRIVATE_KEY
import braintree
from partners.models import Partner


braintree.Configuration.configure(braintree.Environment.Sandbox,
    merchant_id=BRAINTREE_MERCHANT_ID,
    public_key=BRAINTREE_PUBLIC_KEY,
    private_key=BRAINTREE_PRIVATE_KEY
    )


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
        super(OrderStatus, self).save(*args, **kwargs)


class PaymentStatus(models.Model):
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
        super(PaymentStatus, self).save(*args, **kwargs)


class Order(models.Model):
    status = models.ForeignKey(OrderStatus, blank=True, null=True, default=1) #pending (initiated, but not paid)

    guide = models.ForeignKey(GuideProfile, blank=True, null=True, default=None)
    tourist = models.ForeignKey(TouristProfile, blank=True, null=True, default=None)
    partner = models.ForeignKey(Partner, blank=True, null=True, default=None)

    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)

    #if a guide is booked directly or hourly tour was booked, here goes hourly price and final nmb of hours
    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours_nmb = models.IntegerField(default=0)#if an hourly tour was specified
    number_persons = models.IntegerField(default=1)
    price_per_additional_person = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_person_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)


    #if a fixed-price tour is ordered, its price goes here
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    additional_services_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price_before_fees = models.DecimalField(max_digits=8, decimal_places=2, default=0)#for tourist

    fees_tourist = models.DecimalField(max_digits=8, decimal_places=2, default=0)#additional fees for tourist (increasing)
    fees_guide = models.DecimalField(max_digits=8, decimal_places=2, default=0)#additional fees for guide (decreasing)
    fees_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)#total fees of a company

    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    guide_payment = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=1)

    payment_status = models.ForeignKey(PaymentStatus, blank=True, null=True, default=1)

    rating_tourist = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating_guide = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    comment = models.TextField(blank=True, null=True, default=None)
    date_ordered = models.DateTimeField(auto_now_add=True, auto_now=False)

    date_booked_for = models.DateTimeField(blank=True, null=True, default=None)
    date_toured = models.DateField(blank=True, null=True, default=None)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def __str__(self):
        if self.guide:
            return "%s %s" % (self.id, self.guide.user.generalprofile.first_name)
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
        price_after_discount = float(self.price) - float(self.discount)
        self.price_after_discount = price_after_discount

        self.total_price_before_fees = price_after_discount + float(self.additional_services_price) + float(self.additional_person_total)

        if not self.currency and self.guide.currency:
            self.currency = self.guide.currency

        #FEES RATES FOR TOURISTS AND GUIDES
        fees_tourist_rate = float(0.13)
        fees_guide_rate = float(0.13)
        fees_tourist = float(self.total_price_before_fees)*fees_tourist_rate
        fees_guide = float(self.total_price_before_fees)*fees_guide_rate

        self.fees_tourist = fees_tourist
        self.fees_guide = fees_guide
        self.fees_total = fees_tourist + fees_guide
        self.total_price = float(self.total_price_before_fees) + fees_tourist
        self.guide_payment = float(self.total_price_before_fees) - fees_guide
        super(Order, self).save(*args, **kwargs)


    def making_order_payment(self):
        order = self
        payment_method = PaymentMethod.objects.filter(is_active=True).order_by('is_default', '-id').first()

        print("payment method: %s" % payment_method.token)

        print(self.total_price)
        amount = "%s" % float(self.total_price)
        print(amount)

        result = braintree.Transaction.sale({
            "amount": amount,
            "payment_method_token": payment_method.token,
            "options": {
                "submit_for_settlement": False
            }
        })

        # print (result)

        if result.is_success:
            data = result.transaction

            payment_uuid = data.id
            amount = data.amount
            currency = data.currency_iso_code
            currency, created = Currency.objects.get_or_create(name=currency)

            Payment.objects.create(order=order, payment_method=payment_method,
                                   uuid=payment_uuid, amount=amount, currency=currency)

            order.status_id = 5 # payment reserved
            order.payment_status_id = 2 #full payment reserverd

            order.save(force_update=True)

            return {"result": True}

        else:
            return {"result": False}

    def making_mutual_agreement(self):
        order = self
        order.status_id = 9 # mutual agreemnt type
        order.save(force_update=True)
        return {"result": True}


"""
saving ratings from review to Order object
"""
@disable_for_loaddata
def order_post_save(sender, instance, created, **kwargs):
    guide = instance.guide

    statistic_info = guide.order_set.filter(review__is_tourist_feedback=True)\
        .aggregate(rating=Avg("rating_guide"), reviews_nmb=Count("id"))
    print (statistic_info)

    if statistic_info["rating"] and statistic_info["reviews_nmb"]:
        guide.orders_with_review_nmb = statistic_info["reviews_nmb"]
        guide.rating = statistic_info["rating"]
        guide.save(force_update=True)


    #sening email according to orders changing
    current_request = CrequestMiddleware.get_request()
    user = current_request.user
    is_guide_saving = True if instance.guide.user == user else False

    if instance._original_fields["status"] and int(instance.status_id) != instance._original_fields["status"].id and int(instance.status_id) != 1:#exclude pending status
        # print ("pre sending")
        data = {"order": instance, "is_guide_saving": is_guide_saving}
        SendingEmail(data).email_for_order()

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

    def __str__(self):
        if self.service:
            return "%s" % (self.service.name)
        else:
            return "%s" % (self.id)

    def save(self, *args, **kwargs):
        self.price_after_discount = self.discount
        super(ServiceInOrder, self).save(*args, **kwargs)

"""
saving sum of all additional services to order
"""
@disable_for_loaddata
def service_in_order_post_save(sender, instance, created, **kwargs):

    #! Double check how this functionality works
    order = instance.order
    additional_services = order.serviceinorder_set.filter(is_active=True)\
        .aggregate(total_price = Sum('price_after_discount'))

    additional_services_total_price = additional_services.get("total_price", 0)
    order.additional_services_price = additional_services_total_price
    order.save(force_update=True)

post_save.connect(service_in_order_post_save, sender=ServiceInOrder)


class Review(models.Model):
    order = models.OneToOneField(Order, blank=True, null=True, default=None)

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

    def __str__(self):
        if self.order:
            if self.order.tour:
                return "%s" % self.order.tour.name
            else:
                return "%s" % self.order.guide.user.generalprofile.first_name
        else:
            return "%s" % self.id

    def save(self, *args, **kwargs):
        super(Review, self).save(*args, **kwargs)


"""
saving ratings from review to Order object
"""
@disable_for_loaddata
def review_post_save(sender, instance, created, **kwargs):
    order = instance.order
    order.rating_tourist = instance.guide_rating
    order.rating_guide = instance.tourist_rating
    order.save(force_update=True)

post_save.connect(review_post_save, sender=Review)
