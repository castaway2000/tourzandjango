from django.contrib import admin
from .models import *


class BannerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Banner._meta.fields]

    class Meta:
        model = Banner
admin.site.register(Banner, BannerAdmin)