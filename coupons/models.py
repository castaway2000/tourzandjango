from django.db import models
from django.contrib.auth.models import User
from utils.general import uuid_size_6_creating, uuid_creating
from guides.models import GuideProfile


class Campaign(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    date_since = models.DateTimeField(blank=True, null=True)
    date_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.name


class CouponType(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class Coupon(models.Model):
    uuid = models.CharField(max_length=48, blank=True, null=True, default=None)
    value = models.IntegerField(default=0)
    code = models.CharField(max_length=32, blank=True, null=True)
    type = models.ForeignKey(CouponType, blank=True, null=True, default=None)
    user_limit = models.IntegerField(default=0)
    campaign = models.ForeignKey(Campaign, blank=True, null=True, default=None)
    guide = models.ForeignKey(GuideProfile, blank=True, null=True, default=None)

    def __str__(self):
        return "%s" % self.code

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            self.code = self.create_code()
        if not self.uuid:
            self.uuid = uuid_creating()
        super(Coupon, self).save(*args, **kwargs)

    def get_discount_amount_for_amount(self, amount):
        if self.type and self.type.name == 'percentage':
            return (float(amount)*float(self.value))/100
        elif self.type and self.type.name == "fix":
            return float(amount + self.value)
        else:
            return 0

    def create_code(self):
        code = uuid_size_6_creating()
        if Coupon.objects.filter(code=code).exists():
            return self.create_code()
        else:
            return code

    def get_coupon_data(self):
        coupon = self
        coupon_type = coupon.type.name if coupon.type else None
        coupon_amount = coupon.value
        coupon_type_data = 'in virtual cash'
        if coupon_type == 'percentage':
            coupon_type_data = '% off your next booking'
        elif coupon_type == 'monetary':
            coupon_type_data = '$ off your next booking'
        coupon_data = '{} - {}{}'.format(coupon, coupon_amount, coupon_type_data)
        return coupon_data

    def create_coupon_uuid(self):
        if not self.uuid:
            uuid = uuid_creating()
            self.uuid = uuid
            self.save(force_update=True)
            return uuid
        else:
            return self.uuid

    def get_if_more_users_available(self):
        user_limit = self.user_limit
        nmb_redeemed = CouponUser.objects.filter(redeemed_at__isnull=True).count()
        if user_limit == 0:
            return True
        elif user_limit > nmb_redeemed:
            return True
        else:
            return False

    def get_if_guide_coupon(self):
        if self.guide:
            return True
        else:
            return False


class CouponUser(models.Model):
    user = models.ForeignKey(User)
    coupon = models.ForeignKey(Coupon)
    redeemed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s: %s" % (self.user, self.coupon.code)