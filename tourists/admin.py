from django.contrib import admin
from .models import *


class TouristProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TouristProfile._meta.fields]

    class Meta:
        model = TouristProfile

admin.site.register(TouristProfile, TouristProfileAdmin)


class TouristTravelPhotoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TouristTravelPhoto._meta.fields]

    class Meta:
        model = TouristTravelPhoto

admin.site.register(TouristTravelPhoto, TouristTravelPhotoAdmin)

