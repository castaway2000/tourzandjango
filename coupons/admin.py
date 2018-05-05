from django.contrib import admin
from .models import *


class CampaignAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Campaign._meta.fields]

    class Meta:
        model = Campaign

admin.site.register(Campaign, CampaignAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Coupon._meta.fields]

    class Meta:
        model = Coupon

admin.site.register(Coupon, CouponAdmin)


class CouponUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CouponUser._meta.fields]

    class Meta:
        model = CouponUser

admin.site.register(CouponUser, CouponUserAdmin)