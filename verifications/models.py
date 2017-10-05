from django.db import models
from django.contrib.auth.models import User
from utils.uploadings import upload_path_handler_user_scanned_docs
from users.models import GeneralProfile


class IdentityVerification(models.Model):
    general_profile = models.OneToOneField(GeneralProfile)
    onfido_id = models.CharField(max_length=64, null=True)
    checks_url = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class VerificationReportType(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class VerificationReportStatus(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class VerificationReportResult(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class IdentityVerificationReport(models.Model):
    identification_checking = models.ForeignKey(IdentityVerification)
    report_url = models.CharField(max_length=256, null=True)
    type = models.ForeignKey(VerificationReportType, blank=True, null=True, default=None)
    status = models.ForeignKey(VerificationReportStatus, blank=True, null=True, default=None)
    result = models.ForeignKey(VerificationReportResult, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class DocumentType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class ScanStatus(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class DocumentScan(models.Model):
    general_profile = models.ForeignKey(GeneralProfile)
    # user = models.ForeignKey(User, blank=True, null=True, default=None)
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, default=None)
    file = models.FileField(upload_to=upload_path_handler_user_scanned_docs, blank=True, null=True, default=None)
    status = models.ForeignKey(ScanStatus, blank=True, null=True, default=1)#status 1 - "new", 2 - "approved", 3 - "rejected"
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.document_type:
            return "%s %s" % (self.general_profile.user.username, self.document_type.name)
        else:
            return "%s" % self.general_profile.user.username