from django.contrib import admin
from .models import *


class GeoTrackerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GeoTracker._meta.fields]

    class Meta:
        model = GeoTracker

admin.site.register(GeoTracker, GeoTrackerAdmin)


class GeoTripAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GeoTrip._meta.fields]

    class Meta:
        model = GeoTrip

admin.site.register(GeoTrip, GeoTripAdmin)


class GeoChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GeoChat._meta.fields]

    class Meta:
        model = GeoChat

admin.site.register(GeoChat, GeoChatAdmin)


class GeoChatMessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GeoChatMessage._meta.fields]

    class Meta:
        model = GeoChatMessage

admin.site.register(GeoChatMessage, GeoChatMessageAdmin)


class WaitlistAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Waitlist._meta.fields]

    class Meta:
        model = Waitlist

admin.site.register(Waitlist, WaitlistAdmin)
