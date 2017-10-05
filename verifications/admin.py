from django.contrib import admin
from .models import *


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