from django.contrib import admin
from .models import *


class TourIncludedItemInline(admin.TabularInline):
    model = TourIncludedItem
    extra = 0


class TourExcludedItemInline(admin.TabularInline):
    model = TourExcludedItem
    extra = 0


class TourProgramItemInline(admin.TabularInline):
    model = TourProgramItem
    extra = 0


class ScheduledTourInline(admin.TabularInline):
    model = ScheduledTour
    extra = 0


class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentType._meta.fields]

    class Meta:
        model = PaymentType

admin.site.register(PaymentType, PaymentTypeAdmin)


class TourAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tour._meta.fields]
    inlines = [TourIncludedItemInline, TourExcludedItemInline, TourProgramItemInline, ScheduledTourInline]

    class Meta:
        model = Tour

admin.site.register(Tour, TourAdmin)


class TourIncludedItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourIncludedItem._meta.fields]

    class Meta:
        model = TourIncludedItem

admin.site.register(TourIncludedItem, TourIncludedItemAdmin)


class TourExcludedItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourExcludedItem._meta.fields]

    class Meta:
        model = TourExcludedItem

admin.site.register(TourExcludedItem, TourExcludedItemAdmin)


class TourProgramItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourProgramItem._meta.fields]

    class Meta:
        model = TourProgramItem

admin.site.register(TourProgramItem, TourProgramItemAdmin)


class ScheduledTourAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ScheduledTour._meta.fields]

    class Meta:
        model = ScheduledTour

admin.site.register(ScheduledTour, ScheduledTourAdmin)


class TourImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourImage._meta.fields]

    class Meta:
        model = TourImage

admin.site.register(TourImage, TourImageAdmin)


class ScheduleTemplateItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ScheduleTemplateItem._meta.fields]

    class Meta:
        model = ScheduleTemplateItem

admin.site.register(ScheduleTemplateItem, ScheduleTemplateItemAdmin)