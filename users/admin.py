from django.contrib import admin
from .models import *


class InterestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Interest._meta.fields]

    class Meta:
        model = Interest

admin.site.register(Interest, InterestAdmin)


# class UserInterestAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in UserInterest._meta.fields]
#
#     class Meta:
#         model = UserInterest
#
# admin.site.register(UserInterest, UserInterestAdmin)
