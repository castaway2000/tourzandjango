from django.contrib import admin
from .models import *


class DocumentScanInline(admin.TabularInline):
        model = DocumentScan
        extra = 0


class GuideProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuideProfile._meta.fields]
    inlines = [DocumentScanInline]

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
