from django.contrib import admin
from .models import *


class BannerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Banner._meta.fields]

    class Meta:
        model = Banner

admin.site.register(Banner, BannerAdmin)


class NotificationSubjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NotificationSubject._meta.fields]

    class Meta:
        model = NotificationSubject

admin.site.register(NotificationSubject, NotificationSubjectAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Notification._meta.fields]

    class Meta:
        model = Notification

admin.site.register(Notification, NotificationAdmin)