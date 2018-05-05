from django.db import models
from django.contrib.auth.models import User
from utils.general import uuid_size_6_creating


class Campaign(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class CouponType(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class Coupon(models.Model):
    value = models.IntegerField(default=0)
    code = models.CharField(max_length=32, blank=True, null=True)
    type = models.ForeignKey(CouponType, blank=True, null=True, default=None)
    user_limit = models.IntegerField(default=0)
    campaign = models.ForeignKey(Campaign, blank=True, null=True, default=None)

    def __str__(self):
        return "%s" % self.code

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            self.code = self.uuid_size_6_creating()
        super(Coupon, self).save(*args, **kwargs)

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


class CouponUser(models.Model):
    user = models.ForeignKey(User)
    coupon = models.ForeignKey(Coupon)
    redeemed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s: %s" % (self.user, self.coupon.code)