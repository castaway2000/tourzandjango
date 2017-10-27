from django.contrib import admin
from .models import *


class IdentityVerificationApplicantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IdentityVerificationApplicant._meta.fields]

    class Meta:
        model = IdentityVerificationApplicant

admin.site.register(IdentityVerificationApplicant, IdentityVerificationApplicantAdmin)


class IdentityVerificationCheckAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IdentityVerificationCheck._meta.fields]

    class Meta:
        model = IdentityVerificationCheck

admin.site.register(IdentityVerificationCheck, IdentityVerificationCheckAdmin)


class VerificationReportTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VerificationReportType._meta.fields]

    class Meta:
        model = VerificationReportType

admin.site.register(VerificationReportType, VerificationReportTypeAdmin)


class VerificationReportStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VerificationReportStatus._meta.fields]

    class Meta:
        model = VerificationReportStatus

admin.site.register(VerificationReportStatus, VerificationReportStatusAdmin)


class VerificationReportResultAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VerificationReportResult._meta.fields]

    class Meta:
        model = VerificationReportResult

admin.site.register(VerificationReportResult, VerificationReportResultAdmin)


class IdentityVerificationReportAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IdentityVerificationReport._meta.fields]

    class Meta:
        model = IdentityVerificationReport

admin.site.register(IdentityVerificationReport, IdentityVerificationReportAdmin)


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


# class DocumentScanAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in DocumentScan._meta.fields]
#
#     class Meta:
#         model = DocumentScan
#
# admin.site.register(DocumentScan, DocumentScanAdmin)


class WebhookLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WebhookLog._meta.fields]

    class Meta:
        model = WebhookLog

admin.site.register(WebhookLog, WebhookLogAdmin)