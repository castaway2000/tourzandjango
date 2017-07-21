from django.contrib import admin
from .models import *


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


class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DocumentType._meta.fields]

    class Meta:
        model = DocumentType

admin.site.register(DocumentType, DocumentTypeAdmin)


class ScanStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ScanStatus._meta.fields]

    class Meta:
        model = ScanStatus

admin.site.register(ScanStatus, ScanStatusAdmin)


class DocumentScanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DocumentScan._meta.fields]

    class Meta:
        model = DocumentScan

admin.site.register(DocumentScan, DocumentScanAdmin)