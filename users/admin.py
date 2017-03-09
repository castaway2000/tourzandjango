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