from django.contrib import admin
from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]

    class Meta:
        model = Profile

admin.site.register(Profile, ProfileAdmin)


class GuideProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideProfile._meta.fields]

    class Meta:
        model = GuideProfile

admin.site.register(GuideProfile, GuideProfileAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]

    class Meta:
        model = Service

admin.site.register(Service, ServiceAdmin)


class ServiceGuideAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceGuide._meta.fields]

    class Meta:
        model = ServiceGuide

admin.site.register(ServiceGuide, ServiceGuideAdmin)