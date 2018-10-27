from django.db import models


class Banner(models.Model):
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=240)
    url = models.URLField(default=None, null=True)
    call_to_action = models.CharField(max_length=32, default='')
    active = models.BooleanField(default=False)