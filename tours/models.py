from __future__ import unicode_literals

from django.db import models
from django.contrib.sitemaps import ping_google
from django.contrib.auth.models import User
from locations.models import Location, Currency, City
from utils.uploadings import *
from django.utils.text import slugify
from utils.general import random_string_creating
from guides.models import GuideProfile
from utils.images_resizing import optimize_size
import datetime
from utils.general import uuid_creating
from django.utils.translation import ugettext as _
from django.db.models import Sum, Min


class PaymentType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class Tour(models.Model):
    SCHEDULED = "1"
    PRIVATE = "2"
    TOUR_TYPES = (
        (SCHEDULED, _("Scheduled - this tour must take place with any number of participants on schedule.")),
        (PRIVATE, _("Private - this tour must take place in the custom date and time after your negotiation with a tourist and approve it."))
    )

    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    overview_short = models.TextField(blank=True, null=True, default=None)
    overview = models.TextField(blank=True, null=True, default=None)
    included = models.TextField(blank=True, null=True, default=None)
    excluded = models.TextField(blank=True, null=True, default=None)
    image = models.ImageField(upload_to=upload_path_handler_tour, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_tour_large, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_tour_medium, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_tour_small, blank=True, null=True, default=None)

    guide = models.ForeignKey(GuideProfile)
    city = models.ForeignKey(City, blank=True, null=True, default=None)
    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    #scheduled or private tour
    type = models.CharField(max_length=12, blank=True, null=True, default=PRIVATE, choices=TOUR_TYPES)

    #for Scheduled fixed price tours
    currency = models.ForeignKey(Currency, blank=True, null=True, default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hours = models.IntegerField(default=0)

    #for Private FIXED price tours
    persons_nmb_for_min_price = models.IntegerField(default=2)
    max_persons_nmb = models.IntegerField(default=10)
    additional_person_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    #for Private HOURLY tours
    price_hourly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    min_hours = models.IntegerField(default=0)

    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)#in decimals
    price_final = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    payment_type = models.ForeignKey(PaymentType, blank=True, null=True, default=None)#hourly or fixed price
    slug = models.SlugField(max_length=200, blank=True, null=True, default=random_string_creating)

    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "%s %s" % (self.id, self.name)
        else:
            return "%s" % self.id

    def __init__(self, *args, **kwargs):
        super(Tour, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass


    def save(self, *args, **kwargs):
        if not self.payment_type:
            self.payment_type_id = 2#fixed price

        self.price_final = self.price - self.discount

        if not self.city and self.guide.city:
            self.city == self.guide.city

        if not self.uuid:
            self.uuid = uuid_creating()

        self.slug = slugify(self.name)

        if self.payment_type_id == 1: #hourly

            self.price = 0
            self.hours = 0
            self.is_free = False

        if self.payment_type_id == 2: #paid

            self.price_hourly = 0
            self.min_hours = 0
            self.is_free = False

        if self.payment_type_id == 3: #free
            self.is_free = True

            self.price = 0
            self.hours = 0
            self.price_hourly = 0
            self.min_hours = 0

        if self._original_fields["image"] != self.image or (self.image and (not self.image_medium or not self.image_small)):
            self.image_small = optimize_size(self.image, "small")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_large = optimize_size(self.image, "large")

        super(Tour, self).save(*args, **kwargs)
        try:
            ping_google()
        except Exception:
            pass

    def get_hours_nmb_range(self):
        min_hours_nmb = self.min_hours

        min_hours_nmb_range_basic = range(min_hours_nmb, min_hours_nmb+5)
        min_hours_nmb_range_full = range(min_hours_nmb, min_hours_nmb+10)

        return {"min_hours_nmb_range_basic": min_hours_nmb_range_basic,
                "min_hours_nmb_range_full": min_hours_nmb_range_full}

    def get_absolute_url(self):
        # return reverse('tour', kwargs={'name': self.name, 'tour_id': self.id})
        return '/tour/%s/%s/' % (self.slug, self.id)

    def get_included_items(self):
        included_items = self.tourincludeditem_set.filter(is_active=True).order_by("order_priority", "id")
        return included_items

    def get_excluded_items(self):
        excluded_items = self.tourexcludeditem_set.filter(is_active=True).order_by("order_priority", "id")
        return excluded_items

    def get_tourprogram_items(self):
        program_items = self.tourprogramitem_set.filter(is_active=True).order_by("day", "time")
        return program_items

    def get_nearest_available_dates(self, days_nmb=None):
        now = datetime.datetime.now()
        if days_nmb:
            period_end = now + datetime.timedelta(days=days_nmb)
            scheduled_tours = self.scheduledtour_set.filter(is_active=True, dt__gte=now, dt__lte=period_end).order_by("dt")
        else:
            scheduled_tours = self.scheduledtour_set.filter(is_active=True, dt__gte=now).order_by("dt")[:5]
        return scheduled_tours

    def get_nearest_available_dates_1_item(self):
        return self.get_nearest_available_dates(30)[:1]

    def get_nearest_available_dates_30_days(self):
        return  self.get_nearest_available_dates(30)

    def get_tours_images(self):
        return self.tourimage_set.filter(is_active=True).values()

    def get_reviews(self):
        tour_orders = self.order_set.all()
        reviews = list()
        for order in tour_orders.iterator():
            if hasattr(order, "review") and order.review.is_tourist_feedback == True:
                reviews.append(order.review)
        return reviews

    def get_template_items(self):
        template_items = self.scheduletemplateitem_set.filter(is_active=True, is_general_template=False)
        template_items_dict = dict()
        for template_item in template_items.iterator():
            if template_item.day:
                day = int(template_item.day)
                if not day in template_items_dict:
                    template_items_dict[day] = list()
                template_items_dict[day].append(template_item)
        return template_items_dict

    def get_lowest_scheduled_tour_prices(self):
        nearest_tours = self.get_nearest_available_dates(20)
        if nearest_tours:
            price_final_item = nearest_tours.aggregate(min_price_final=Min('price_final'))
            return price_final_item["min_price_final"]
        else:
            return 0


class TourIncludedItem(models.Model):
    tour = models.ForeignKey(Tour)
    order_priority = models.IntegerField(default=0)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.name)


class TourExcludedItem(models.Model):
    tour = models.ForeignKey(Tour)
    order_priority = models.IntegerField(default=0)
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.name)


class TourProgramItem(models.Model):
    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    day = models.IntegerField(default=1)
    time = models.TimeField()
    duration = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_path_handler_tour_images, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_tour_images, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_tour_images, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_tour_images, blank=True, null=True, default=None)

    def __str__(self):
        return "%s" % (self.name)

    def __init__(self, *args, **kwargs):
        super(TourProgramItem, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid_creating()

        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")
        super(TourProgramItem, self).save(*args, **kwargs)


class ScheduledTour(models.Model):
    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
    tour = models.ForeignKey(Tour)
    dt = models.DateTimeField()
    time_start = models.TimeField(blank=True, null=True, default=None)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_final = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    seats_total = models.IntegerField(default=0)
    seats_booked = models.IntegerField(default=0)
    seats_available = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.dt and self.tour:
            dt = self.dt.strftime('%m/%d/%Y %I:%M')
            return "%s -- %s USD -- %s" % (dt, self.price_final, self.tour.name)
        elif self.tour:
            return "%s" % (self.tour.name)
        else:
            return "%s" % (self.id)

    def __init__(self, *args, **kwargs):
        super(ScheduledTour, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if self.time_start and self.dt:
            self.dt = datetime.datetime.combine(self.dt, self.time_start)

        if not self.uuid:
            self.uuid = uuid_creating()

        if self.discount:
            self.price_final = self.price - self.discount
        else:
            self.price_final = self.price

        if self.seats_available != self._original_fields["seats_available"]:
            #if user changes available places nmb, then we take it as a basis for calculation booked places,
            #if user does not changes this field, we use booked places nmb as a basis for calculation available places
            self.seats_booked = self.seats_total - self.seats_available
        else:
            self.seats_available = self.seats_total - self.seats_booked
        super(ScheduledTour, self).save(*args, **kwargs)

    def get_name(self):
        dt = self.dt.strftime('%m/%d/%Y %I:%M')
        return "%s -- %s USD -- %s" % (dt, self.price_final, self.tour.name)

    def get_tour_end(self):
        tour_hours = self.tour.hours
        if self.dt:
            tour_ends_time = self.dt + datetime.timedelta(hours=tour_hours)
            return tour_ends_time.time()
        else:
            return None

    def has_pending_reserved_bookings(self):
        return self.order_set.filter(status__in=[2, 5]).exists() #pending, agreed, payment_reserved

    def get_pending_reserved_seats(self):
        #pending seats from bookings in payment reserved status
        pending_orders = self.order_set.filter(status__in=[5]).aggregate(nmb_seats=Sum("number_persons"))
        return pending_orders["nmb_seats"] if pending_orders["nmb_seats"] else 0

    def get_all_orders(self):
        return self.order_set.all().exclude(status_id=1).order_by("-id")


class ScheduleTemplateItem(models.Model):
    DAYS = (
                ('0', 'Monday'),
                ('1', 'Tuesday'),
                ('2', 'Wednesday'),
                ('3', 'Thursday'),
                ('4', 'Friday'),
                ('5', 'Saturday'),
                ('6', 'Sunday'),
            )
    tour = models.ForeignKey(Tour)
    day = models.CharField(max_length=1, blank=True, null=True, default=None, choices=DAYS)
    time_start = models.TimeField(blank=True, null=True, default=None)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    seats_total = models.IntegerField(default=0)
    is_general_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Schedule Template Item'
        verbose_name_plural = 'Schedule Template Items'

    def populate_weekdays(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for index, day in enumerate(days):
            ScheduleTemplateItem.objects.update_or_create(tour=self.tour, day=index, time_start=self.time_start,
                                                            is_general_template=False, is_active=True,
                                                            defaults={"time_start": self.time_start, "price": self.price,
                                                                      "seats_total": self.seats_total
                                                                      }
                                                          )


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, blank=True, null=True)
    image = models.ImageField(upload_to=upload_path_handler_tour_images)
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.tour.name

    """
    reading of initial values for fields to compare them with values on save if needed
    """
    def __init__(self, *args, **kwargs):
        super(TourImage, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):

        if not self.pk:
            print("self.pk")
            print(self.tour.image.url)

            if self.tour.image.url.endswith("default_tour_image.jpg"):
                self.tour.image = self.image
                self.tour.save(force_update=True)

                self.is_main = True
        else:
            """
            setting an image on tour instance if it is set here
            """
            for field in self._meta.local_fields:
                if field.name == "is_main" and self.tour:
                    old = self._original_fields[field.name]
                    new = getattr(self, field.name)
                    if old != new and new == True:#if new value is True

                        #put is_main flag to False to other possible existing images
                        self.tour.tourimage_set.filter(is_main=True).update(is_main=False)
                        self.tour.image = self.image
                        self.tour.save(force_update=True)

        super(TourImage, self).save(*args, **kwargs)
