from django.contrib import admin
from .models import *


class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentType._meta.fields]

    class Meta:
        model = PaymentType

admin.site.register(PaymentType, PaymentTypeAdmin)


class TourAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tour._meta.fields]

    class Meta:
        model = Tour

admin.site.register(Tour, TourAdmin)


class TourImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourImage._meta.fields]

    class Meta:
        model = TourImage

admin.site.register(TourImage, TourImageAdmin)


# class ReviewAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Review._meta.fields]
#
#     class Meta:
#         model = Review
#
# admin.site.register(Review, ReviewAdmin)