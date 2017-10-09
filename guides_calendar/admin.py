from django.contrib import admin
from .models import *


class CalendarItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CalendarItem._meta.fields]

    class Meta:
        model = CalendarItem

admin.site.register(CalendarItem, CalendarItemAdmin)


class CalendarItemGuideAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CalendarItemGuide._meta.fields]

    class Meta:
        model = CalendarItemGuide

admin.site.register(CalendarItemGuide, CalendarItemGuideAdmin)


class CalendarItemStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CalendarItemStatus._meta.fields]

    class Meta:
        model = CalendarItemStatus

admin.site.register(CalendarItemStatus, CalendarItemStatusAdmin)


class ScheduleTemplateItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ScheduleTemplateItem._meta.fields]

    class Meta:
        model = ScheduleTemplateItem

admin.site.register(ScheduleTemplateItem, ScheduleTemplateItemAdmin)