from django.contrib import admin
from .models import *


class CountryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Country._meta.fields]
    readonly_fields = ["slug", "image_large", "image_medium", "image_small"]

    class Meta:
        model = Country

admin.site.register(Country, CountryAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in City._meta.fields]
    readonly_fields = ["slug", "image_large", "image_medium", "image_small"]

    class Meta:
        model = City

admin.site.register(City, CityAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Currency._meta.fields]

    class Meta:
        model = Currency

admin.site.register(Currency, CurrencyAdmin)


class SearchLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SearchLog._meta.fields]

    class Meta:
        model = SearchLog

admin.site.register(SearchLog, SearchLogAdmin)


class NewLocationTourRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NewLocationTourRequest._meta.fields]
    class Meta:
        model = NewLocationTourRequest

admin.site.register(NewLocationTourRequest, NewLocationTourRequestAdmin)