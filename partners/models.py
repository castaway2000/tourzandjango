from django.db import models
from utils.general import uuid_creating
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from utils.sending_emails import SendingEmail


class Partner(models.Model):
    uuid = models.CharField(max_length=48, null=True)
    company_name = models.TextField(null=True)
    billing_address = models.CharField(max_length=256, null=True)
    tax_id = models.CharField(max_length=48, null=True)
    website = models.CharField(max_length=128, blank=True, null=True, default=None)
    reason_requesting = models.TextField(null=True)
    traffic = models.CharField(max_length=256, null=True)
    requesting_person = models.CharField(max_length=256, null=True)
    email = models.EmailField(null=True)
    is_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    user = models.OneToOneField(User, null=True)

    def __init__(self, *args, **kwargs):
        super(Partner, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if not self.uuid or self.uuid == "":
            self.uuid = uuid_creating()

        if self.is_confirmed == True and self.is_confirmed != self._original_fields["is_confirmed"]:
            if self.is_active == False:
                self.is_active = True

            user, created = User.objects.get_or_create(username=self.uuid, email=self.email)
            self.user = user

            #a model with API tokens has OneToOne relation with User model, so no need to dublicate it on Partner model
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "api_token": token,
                "user_id": self.user.id
            }
            SendingEmail(data=data).email_for_partners()
        super(Partner, self).save(*args, **kwargs)


class IntegrationPartners(models.Model):
    name = models.TextField(null=True)
    url = models.URLField(null=True)
    logo = models.ImageField(null=True)
    is_active = models.BooleanField(default=False)


class Endorsement(models.Model):
    name = models.TextField(null=True)
    url = models.URLField(null=True)
    logo = models.ImageField(null=True)
    is_active = models.BooleanField(default=False)
