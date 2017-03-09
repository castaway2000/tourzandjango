from django.contrib import admin
from .models import *


class CityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in City._meta.fields]

    class Meta:
        model = City

admin.site.register(City, CityAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Currency._meta.fields]

    class Meta:
        model = Currency

admin.site.register(Currency, CurrencyAdmin)