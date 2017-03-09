from django.contrib import admin
from .models import *


class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentType._meta.fields]

    class Meta:
        model = PaymentType

admin.site.register(PaymentType, PaymentTypeAdmin)


class TourAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tour._meta.fields]
    readonly_fields = ["payment_type"]

    class Meta:
        model = Tour

admin.site.register(Tour, TourAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Review._meta.fields]

    class Meta:
        model = Review

admin.site.register(Review, ReviewAdmin)