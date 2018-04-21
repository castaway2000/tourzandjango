from django.db import models
from django.contrib.auth.models import User
from utils.uploadings import upload_path_handler_user_scanned_docs
from users.models import GeneralProfile
from utils.sending_emails import SendingEmail
from tourzan.storage_backends import PrivateMediaStorageSameLocation


class IdentityVerificationApplicant(models.Model):
    general_profile = models.OneToOneField(GeneralProfile, related_name="user_verification")
    applicant_id = models.CharField(max_length=64, null=True)
    applicant_url = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.general_profile.user


class IdentityVerificationCheck(models.Model):
    applicant = models.ForeignKey(IdentityVerificationApplicant, blank=True, null=True, default=None)
    check_id = models.CharField(max_length=64, null=True)
    check_url = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.applicant


class VerificationReportType(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class VerificationReportStatus(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class VerificationReportResult(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class IdentityVerificationReport(models.Model):
    identification_checking = models.ForeignKey(IdentityVerificationCheck)
    report_id = models.CharField(max_length=64, null=True)
    report_url = models.CharField(max_length=256, null=True)
    type = models.ForeignKey(VerificationReportType, blank=True, null=True, default=None)
    status = models.ForeignKey(VerificationReportStatus, blank=True, null=True, default=None)
    result = models.ForeignKey(VerificationReportResult, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __init__(self, *args, **kwargs):
        super(IdentityVerificationReport, self).__init__(*args, **kwargs)
        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def __str__(self):
        return "%s" % self.report_id

    def save(self, *args, **kwargs):
        if not self.pk or self.result != self._original_fields["result"]:
            general_profile = self.identification_checking.applicant.general_profile


            #changing of verification status, when report status is changing and report result is "clear" and
            #when status is complete
            #If there are 2 reports in the ongoing check, is_verified status will be given only if 2 reports will match
            #conditiions, mentioned above.
            if general_profile.is_verified == False and self.status and self.status.name =="complete" \
                    and self.result and self.result.name == "clear":  # TODO: remove consider after more data is in place to support this works
                remaining_verification_reports = IdentityVerificationReport.objects.filter(identification_checking=self.identification_checking).exclude(status__name="complete", result__name = "clear")
                if self.pk:
                    remaining_verification_reports = remaining_verification_reports.exclude(id=self.pk)
                if not remaining_verification_reports.exists():
                    general_profile.is_verified = True
                    general_profile.save(force_update=True)
                    data = {'user_id': general_profile.user.id}
                    SendingEmail(data=data).email_for_verficiation()

        super(IdentityVerificationReport, self).save(*args, **kwargs)


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
    # test_field = models.CharField(max_length=12, null=True)
    general_profile = models.ForeignKey(GeneralProfile, blank=True, null=True, default=None)
    # user = models.ForeignKey(User, blank=True, null=True, default=None)
    document_type = models.ForeignKey(DocumentType, blank=True, null=True, default=None)
    file = models.FileField(upload_to=upload_path_handler_user_scanned_docs, blank=True, null=True, default=None,
                            storage=PrivateMediaStorageSameLocation())
    status = models.ForeignKey(ScanStatus, blank=True, null=True, default=1)#status 1 - "new", 2 - "approved", 3 - "rejected"
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.document_type:
            return "%s %s" % (self.general_profile.user.username, self.document_type.name)
        else:
            return "%s" % self.general_profile.user.username


class WebhookLog(models.Model):
    url = models.CharField(max_length=256)
    is_successfully_processed = models.BooleanField(default=False)
    error_text = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return "%s" % self.id
