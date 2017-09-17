from django.db import models
from utils.general import uuid_creating


class Partner(models.Model):
    name = models.CharField(max_length=128)
    uuid = models.CharField(max_length=48, null=True)
    website = models.URLField(blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.uuid or self.uuid == "":
            self.uuid = uuid_creating()
        super(Partner, self).save(*args, **kwargs)

