from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class InterestResource(resources.ModelResource):
    class Meta:
        model = Interest


class GroupedInterestResource(resources.ModelResource):
    class Meta:
        model = GroupedInterest


class InterestAdmin(ImportExportModelAdmin):
    resource_class = InterestResource
    list_display = [field.name for field in Interest._meta.fields]

    class Meta:
        model = Interest

admin.site.register(Interest, InterestAdmin)


class GroupedInterestAdmin(ImportExportModelAdmin):
    resource_class = GroupedInterestResource
    list_display = [field.name for field in Interest._meta.fields]

    class Meta:
        model = GroupedInterest

admin.site.register(GroupedInterest, GroupedInterestAdmin)


class UserInterestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserInterest._meta.fields]

    class Meta:
        model = UserInterest

admin.site.register(UserInterest, UserInterestAdmin)


class LanguageLevelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LanguageLevel._meta.fields]

    class Meta:
        model = LanguageLevel

admin.site.register(LanguageLevel, LanguageLevelAdmin)


class UserLanguageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserLanguage._meta.fields]

    class Meta:
        model = UserLanguage

admin.site.register(UserLanguage, UserLanguageAdmin)


class GeneralProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GeneralProfile._meta.fields]

    class Meta:
        model = GeneralProfile

admin.site.register(GeneralProfile, GeneralProfileAdmin)


class SmsSendingHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SmsSendingHistory._meta.fields]

    class Meta:
        model = SmsSendingHistory

admin.site.register(SmsSendingHistory, SmsSendingHistoryAdmin)