import random
from time import time
from hashlib import md5
from django.conf import settings
from django.db import IntegrityError
from django.db import models
from django.dispatch import Signal
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .settings import (
    COUPON_TYPES,
    CODE_LENGTH,
    CODE_CHARS,
    SEGMENTED_CODES,
    SEGMENT_LENGTH,
    SEGMENT_SEPARATOR,
    PRODUCT_MODEL,
    ORDER_MODEL,
)


try:
    user_model = settings.AUTH_USER_MODEL
except AttributeError:
    from django.contrib.auth.models import User as user_model
redeem_done = Signal(providing_args=["coupon"])


class CouponManager(models.Manager):
    def create_coupon(
        self, type, value, users=[], valid_until=None, prefix="",
        campaign=None, user_limit=None, bulk=False, bulk_number=0, bulk_seed=''
    ):
        if bulk and bulk_seed == '':
            bulk_seed = md5(hex(int(time() * 10000000))[2:].encode()).hexdigest()

        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix),
            type=type,
            valid_until=valid_until,
            campaign=campaign,
            bulk=bulk,
            bulk_number=bulk_number,
            bulk_seed=bulk_seed,
        )
        if user_limit is not None:  # otherwise use default value of model
            coupon.user_limit = user_limit
        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            coupon = Coupon.objects.create_coupon(type, value, users, valid_until, prefix, campaign)
        if not isinstance(users, list):
            users = [users]
        for user in users:
            if user:
                CouponUser(user=user, coupon=coupon).save()
        return coupon

    def create_coupons(self, quantity, type, value, valid_until=None, prefix="", campaign=None):
        coupons = []
        for i in range(quantity):
            coupons.append(self.create_coupon(type, value, None, valid_until, prefix, campaign))
        return coupons

    def get_coupon(self, code):
        try:
            return self.get(code__iexact=code)
        except Coupon.DoesNotExist:
            pass
        # Check to see if there's a bulk code with
        bulk_coupons = self.filter(bulk=True)
        for bulk_coupon in bulk_coupons:
            if code.upper().find(bulk_coupon.code.upper()) != 0:
                continue
            # Check coupon sequence ID
            start = len(bulk_coupon.code)
            stop = start + len(hex(bulk_coupon.bulk_number)[2:])
            try:
                index = int(code[start:stop], base=16)
            except ValueError:
                continue
            if index < 0 or index >= bulk_coupon.bulk_number:
                continue

            # Check complete code with seed
            if code.upper() == bulk_coupon.get_bulk_code(index).upper():
                return bulk_coupon

        raise Coupon.DoesNotExist

    def used(self):
        return self.exclude(users__redeemed_at__isnull=True)

    def unused(self):
        return self.filter(users__redeemed_at__isnull=True)

    def expired(self):
        return self.filter(valid_until__lt=timezone.now())


@python_2_unicode_compatible
class Coupon(models.Model):
    code = models.CharField(
        _("Code"), max_length=30, unique=True, blank=True,
        help_text=_("Leaving this field empty will generate a random code."))
    description = models.CharField(max_length=256, blank=True, null=True)
    value = models.DecimalField(
        _("Value"), help_text=_("Arbitrary coupon value"), max_digits=6, decimal_places=2
    )
    type = models.CharField(_("Type"), max_length=20, choices=COUPON_TYPES)
    user_limit = models.PositiveIntegerField(_("User limit"), default=1)
    created_at = models.DateTimeField(_("Created at"), default=timezone.now)
    valid_until = models.DateTimeField(
        _("Valid until"), blank=True, null=True,
        help_text=_("Leave empty for coupons that never expire"))
    active = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        'Campaign', verbose_name=_("Campaign"), blank=True, null=True, related_name='coupons',
        on_delete=models.CASCADE
    )
    bulk = models.BooleanField(default=False)
    bulk_number = models.PositiveIntegerField(default=0)
    bulk_seed = models.CharField(max_length=32, blank=True)
    bulk_length = models.PositiveIntegerField(default=8)

    if PRODUCT_MODEL:
        valid_products = models.ManyToManyField(PRODUCT_MODEL, blank=True)

    objects = CouponManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    def expired(self):
        return self.valid_until is not None and self.valid_until < timezone.now()

    @property
    def is_redeemed(self):
        """ Returns true is a coupon is redeemed (completely for all users) otherwise returns false. """
        if not self.bulk:
            return self.users.filter(
                redeemed_at__isnull=False
            ).count() >= self.user_limit and self.user_limit is not 0
        else:
            return self.users.filter(
                redeemed_at__isnull=False
            ).count() >= self.bulk_number

    @property
    def redeemed_at(self):
        try:
            return self.users.filter(redeemed_at__isnull=False).order_by('redeemed_at').last().redeemed_at
        except self.users.through.DoesNotExist:
            return None

    @classmethod
    def generate_code(cls, prefix="", segmented=SEGMENTED_CODES):
        code = "".join(random.choice(CODE_CHARS) for i in range(CODE_LENGTH))
        if segmented:
            code = SEGMENT_SEPARATOR.join([code[i:i + SEGMENT_LENGTH] for i in range(0, len(code), SEGMENT_LENGTH)])
            return prefix + code
        else:
            return prefix + code

    def redeem(self, user=None, bulk_code=None):
        try:
            coupon_user = self.users.get(user=user)
        except CouponUser.DoesNotExist:
            try:  # silently fix unbouned or nulled coupon users
                coupon_user = self.users.get(user__isnull=True, redeemed_at=None)
                coupon_user.user = user
            except CouponUser.DoesNotExist:
                coupon_user = CouponUser(coupon=self, user=user)
        coupon_user.redeemed_at = timezone.now()
        coupon_user.code = bulk_code
        coupon_user.save()
        redeem_done.send(sender=self.__class__, coupon=self)

    def get_bulk_code(self, index):
        hex_id = hex(index)[2:].rjust(len(hex(self.bulk_number)[2:]), '0')
        length = len(self.code) + self.bulk_length
        return str(self.code + hex_id + md5(str(self.bulk_seed + hex_id).encode()).hexdigest()).upper()[0:length]


@python_2_unicode_compatible
class Campaign(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='users', on_delete=models.CASCADE)
    user = models.ForeignKey(user_model, verbose_name=_("User"), null=True, blank=True, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(_("Redeemed at"), blank=True, null=True)
    code = models.CharField(_("Bulk Code"), max_length=64, blank=True, null=True)

    if ORDER_MODEL:
        order = models.ForeignKey(ORDER_MODEL, blank=True, null=True)

    class Meta:
        unique_together = (('coupon', 'user'),)

    def __str__(self):
        return str(self.user)
