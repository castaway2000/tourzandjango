from django.contrib import admin
from .models import *



class GuideProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideProfile._meta.fields]

    class Meta:
        model = GuideProfile

admin.site.register(GuideProfile, GuideProfileAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    readonly_fields = ["html_field_name"]

    class Meta:
        model = Service

admin.site.register(Service, ServiceAdmin)


class GuideServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideService._meta.fields]

    class Meta:
        model = GuideService

admin.site.register(GuideService, GuideServiceAdmin)

