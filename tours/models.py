from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locations.models import Location, Currency, City


class Tour(models.Model):
    user = models.ForeignKey(User)
    city = models.ForeignKey(City, blank=True, null=True, default=None)
    currency = models.ForeignKey(Currency)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_hourly = models.DecimalField(max_digits=8, decimal_places=2)
    min_hours = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return self.id