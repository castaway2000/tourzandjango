from django.contrib import admin
from .models import *
from verifications.models import DocumentScan


class DocumentScanInline(admin.TabularInline):
        model = DocumentScan
        extra = 0


class InterestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Interest._meta.fields]

    class Meta:
        model = Interest

admin.site.register(Interest, InterestAdmin)


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
    inlines = [DocumentScanInline]

    class Meta:
        model = GeneralProfile

admin.site.register(GeneralProfile, GeneralProfileAdmin)


class SmsSendingHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SmsSendingHistory._meta.fields]

    class Meta:
        model = SmsSendingHistory

admin.site.register(SmsSendingHistory, SmsSendingHistoryAdmin)