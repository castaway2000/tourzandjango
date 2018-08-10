from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour, ScheduledTour
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
from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRIVATE_KEY, ON_PRODUCTION
import braintree
from partners.models import Partner
from coupons.models import CouponUser, Coupon, Campaign, CouponType
from utils.general import uuid_creating
import datetime

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
    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
    status = models.ForeignKey(OrderStatus, blank=True, null=True, default=1) #pending (initiated, but not paid)

    guide = models.ForeignKey(GuideProfile, blank=True, null=True, default=None)
    tourist = models.ForeignKey(TouristProfile, blank=True, null=True, default=None)
    partner = models.ForeignKey(Partner, blank=True, null=True, default=None)

    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)
    tour_scheduled = models.ForeignKey(ScheduledTour, blank=True, null=True, default=None)

    #if a guide is booked directly or hourly tour was booked, here goes hourly price and final nmb of hours
    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours_nmb = models.IntegerField(default=0)#if an hourly tour was specified
    #if a fixed-price tour is ordered, its price goes here
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    number_persons = models.IntegerField(default=1)
    number_additional_persons = models.IntegerField(default=0)
    price_per_additional_person = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_person_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_services_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, blank=True, null=True, default=None)

    #20052018 added: it includes tour price + additional person price + additional services price
    total_price_initial = models.DecimalField(max_digits=8, decimal_places=2, default=0)#after discount

    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)#THIS FIELD WILL BE DELETED

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
    date_toured = models.DateTimeField(blank=True, null=True, default=None)

    guide_compensation = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tourist_fees_diff = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    guide_fees_diff = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_discount_on_tourzan_side = models.BooleanField(default=False)
    is_approved_by_guide = models.BooleanField(default=False)
    guide_payout_date = models.DateTimeField(blank=True, null=True, default=None)

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


        """
        the following code is transfered here from making_booking view
        """
        if not self.uuid:
            self.uuid = uuid_creating()

        if not self.pk:
            if not self.guide:
                guide = self.tour.guide
                self.guide = guide
            else:
                guide = self.guide

            tour = self.tour
            number_people = self.number_persons
            if tour:
                if tour.payment_type.id == 1:#hourly
                    self.price_hourly = tour.price_hourly
                    #price as hourly_price*nmb_hours is recalculated below outside of if not self.pk statement

                elif tour.payment_type.id == 2:#fixed
                    if self.tour_scheduled:
                        self.discount = self.tour_scheduled.discount*number_people
                        self.price = self.tour_scheduled.price*number_people
                    else:
                        self.discount = tour.discount

                        #preventing overlimiting for API
                        if number_people > tour.max_persons_nmb:
                            target_people_nmb = tour.max_persons_nmb
                        else:
                            target_people_nmb = number_people

                        persons_nmb_for_min_price_overlimit = target_people_nmb - tour.persons_nmb_for_min_price
                        if persons_nmb_for_min_price_overlimit > 0:
                            self.number_additional_persons = persons_nmb_for_min_price_overlimit

                            self.price_per_additional_person = tour.additional_person_price
                            self.additional_person_total = tour.additional_person_price*persons_nmb_for_min_price_overlimit

                        self.price = tour.price #price final means price after discount
                else:#free tours
                    pass

            else:#guide

                #only for guides, not for tours
                if number_people >= 2 and ((tour and tour.payment_type.id==1) or not tour):#hourly tour or hourly payment for guides
                    guide_additional_person_cost = guide.additional_person_cost
                    self.number_additional_persons = (number_people-1)
                    additional_person_total = guide_additional_person_cost * (number_people-1)#excluding one initial person
                    self.price_per_additional_person = guide.additional_person_cost
                    self.additional_person_total = additional_person_total


                self.price_hourly = guide.rate
                #price as hourly_price*nmb_hours is recalculated below outside of if not self.pk statement

            #getting ref_id from the session
            current_request = CrequestMiddleware.get_request()
            if current_request.session.get("ref_id"):
                ref_id = current_request.session["ref_id"]
                try:
                    partner = Partner.objects.get(uuid=ref_id)
                    kwargs["partner"] = partner
                except:
                    pass


        if self.hours_nmb and self.price_hourly:
            self.price = int(self.hours_nmb) * float(self.price_hourly)

        self.total_price_initial = float(self.price) + float(self.additional_services_price) + float(self.additional_person_total)


        #getting discount if there is a coupon
        if (not self._original_fields["coupon"] and self.coupon) or (self._original_fields["coupon"] and self.coupon and self._original_fields["coupon"].id != self.coupon.id):
            if self.coupon:
                print("get_discount_amount_for_amount")
                self.discount = self.coupon.get_discount_amount_for_amount(self.total_price_initial)
                print(self.discount)

        #calculating tour price
        #this was remade 20052018: now even additional services can be discounted
        self.total_price_before_fees = self.total_price_initial - float(self.discount)

        if not self.currency and self.guide.currency:
            self.currency = self.guide.currency

        #FEES RATES FOR TOURISTS AND GUIDES
        fees_tourist_rate = float(0.13)
        fees_guide_rate = float(0.13)
        fees_tourist = float(self.total_price_before_fees)*fees_tourist_rate
        if self.guide.user.generalprofile.is_fee_free:
            fees_guide = 0
            self.fees_guide = fees_guide
            self.guide_fees_diff = fees_guide - float(self.total_price_before_fees)*fees_guide_rate
        else:
            if self.coupon and self.discount and not self.coupon.get_if_guide_coupon():
                #if it is guide's coupon, discount decreases guide's payment
                total_price_before_fees_without_discount = self.total_price_before_fees + float(self.discount)
                fees_guide_without_discount = total_price_before_fees_without_discount*fees_guide_rate
                fees_guide = fees_guide_without_discount
                self.fees_guide = fees_guide
                self.guide_payment = total_price_before_fees_without_discount - fees_guide_without_discount

                #additional payment to guide from tourzan
                self.guide_compensation = self.guide_payment - (float(self.total_price_before_fees) - float(self.total_price_before_fees)*fees_guide_rate)
                #how much tourzan was not get from tourists fees
                self.guide_fees_diff = fees_guide_without_discount - float(self.total_price_before_fees)*fees_guide_rate
                self.tourist_fees_diff = fees_tourist - (float(total_price_before_fees_without_discount)*fees_tourist_rate)
                self.is_discount_on_tourzan_side = True
            else:
                #old variant before coupons
                #if it is NOT guide's coupon, discount applies only to tourist's payment, but it does not influence amount of initial guide's payment
                fees_guide = float(self.total_price_before_fees)*fees_guide_rate
                self.fees_guide = fees_guide
                self.guide_payment = float(self.total_price_before_fees) - fees_guide

        self.fees_tourist = fees_tourist
        self.fees_total = fees_tourist + fees_guide
        self.total_price = float(self.total_price_before_fees) + fees_tourist

        referred_by = self.tourist.user.generalprofile.referred_by
        if referred_by:
            self.add_statistics_for_referrer()
            self.add_coupon_for_referrer()#checking conditions for possible adding any coupons to referrer

        if self.get_is_full_payment_processed() and self.tour_scheduled:
            self.tour_scheduled.seats_booked += 1
            self.tour_scheduled.save(force_update=True)

        if (self.status.id == 4 or (self.status.id == "4")) and not self._original_fields["status"] in [4, "4"]:
            now = datetime.datetime.now()
            self.date_toured = now
        super(Order, self).save(*args, **kwargs)


    def making_order_payment(self):
        order = self
        payment_method = PaymentMethod.objects.filter(is_active=True).order_by('is_default', '-id').first()
        amount = "%s" % float(self.total_price)
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
            Payment.objects.get_or_create(order=order, payment_method=payment_method,
                                   uuid=payment_uuid, amount=amount, currency=currency)
            order.status_id = 5 # payment reserved
            order.payment_status_id = 2 #full payment reserverd
            order.save(force_update=True)

            if order.is_approved_by_guide:#order details can be approved from chat window by a guide
                order.status_id = 2
                order.save(force_update=True)

            return {"result": True}
        else:
            return {"result": False}

    def making_mutual_agreement(self):
        order = self
        order.status_id = 9 # mutual agreemnt type
        order.save(force_update=True)
        return {"result": True}

    # tourists_with_purchases_referred_nmb
    def add_coupon_for_referrer(self):
        tourist_user = self.tourist.user
        if tourist_user.generalprofile.referred_by:
            referred_by = tourist_user.generalprofile.referred_by
            tourists_with_purchases_referred_nmb = referred_by.generalprofile.tourists_with_purchases_referred_nmb
            nmb_of_tourist_for_coupon = 5
            if tourists_with_purchases_referred_nmb % nmb_of_tourist_for_coupon == 0:
                #here we compare created coupons for this user with referred tourists with purchases
                #this approach will prevent creating a new coupon for a tourist, when the nmb of tourists with purchases
                # was decreased by 1 and then increased by 1
                coupons_user_nmb = CouponUser.objects.filter(user=referred_by, coupon__campaign__name="refer5").count()
                coupons_needed = tourists_with_purchases_referred_nmb / nmb_of_tourist_for_coupon
                if coupons_needed > coupons_user_nmb:
                    campaign, created = Campaign.objects.get_or_create(name="refer5")
                    coupon_type, created = CouponType.objects.get_or_create(name="percentage")
                    coupon = Coupon.objects.create(campaign=campaign, value=20, type=coupon_type, user_limit=1)
                    CouponUser.objects.create(user=referred_by, coupon=coupon)

    def get_is_full_payment_processed(self):
        if (not self._original_fields["payment_status"] or self._original_fields["payment_status"].id != 4) \
            and self.payment_status.id == 4:
            #full payment processed
            return True
        else:
            return False

    def add_statistics_for_referrer(self):
        #Increase or decrease tourist with purchasing
        referred_by = self.tourist.user.generalprofile.referred_by
        if self.get_is_full_payment_processed():
            #increase only if there is no current success payments for this user
            if Order.objects.filter(tourist=self.tourist, payment_status_id=4).count() == 0:
                referred_by.generalprofile.tourists_with_purchases_referred_nmb += 1
                referred_by.generalprofile.save(force_update=True)
        elif self._original_fields["payment_status"] and self._original_fields["payment_status"].id == 4 and self.payment_status.id != 4 \
                and Order.objects.filter(tourist=self.tourist, payment_status_id=4).count() == 1:
            referred_by.generalprofile.tourists_with_purchases_referred_nmb -= 1
            referred_by.generalprofile.save(force_update=True)

    def get_toursit_total_before_discount(self):
        #for showing amount of tourist payment before a discount (initial total amount + tourists fees)
        if self.coupon:
            return self.total_price + self.discount
        else:
            return self.total_price

    def get_order_end(self):
        print("get_order_end")
        tour_hours = self.tour.hours if self.tour else self.hours_nmb
        print(tour_hours)
        if self.date_booked_for:
            tour_ends_time = self.date_booked_for + datetime.timedelta(hours=tour_hours)
            return tour_ends_time.time()
        else:
            return None


"""
saving ratings from review to Order object
"""
@disable_for_loaddata
def order_post_save(sender, instance, created, **kwargs):
    guide = instance.guide

    statistic_info = guide.order_set.filter(review__is_tourist_feedback=True)\
        .aggregate(rating=Avg("rating_guide"), reviews_nmb=Count("id"))

    if statistic_info["rating"] and statistic_info["reviews_nmb"]:
        guide.orders_with_review_nmb = statistic_info["reviews_nmb"]
        guide.rating = statistic_info["rating"]
        guide.save(force_update=True)

    #sening email according to orders changing
    current_request = CrequestMiddleware.get_request()
    if current_request:
        user = current_request.user
        is_guide_saving = True if instance.guide.user == user else False
    else:
        is_guide_saving = False

    if instance._original_fields["status"] and int(instance.status_id) != instance._original_fields["status"].id and int(instance.status_id) != 1:#exclude pending status
        # print ("pre sending")
        data = {"order": instance, "is_guide_saving": is_guide_saving}
        SendingEmail(data).email_for_order()

        if int(instance.status_id) == 2 and instance.tour_scheduled:#agreed
            instance.tour_scheduled.seats_booked += instance.number_persons
            instance.tour_scheduled.save(force_update=True)
        if instance._original_fields["status"].id == 2 and int(instance.status_id) in [3, 6] and instance.tour_scheduled:#if it was agreed and now it is canceled, than reduce booked nmb
            instance.tour_scheduled.seats_booked -= instance.number_persons
            instance.tour_scheduled.save(force_update=True)


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
        self.price_after_discount = self.price - self.discount
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
