from django.db import models
from guides.models import GuideProfile


class CalendarItem(models.Model):
    date = models.DateField(blank=True, null=True, default=None)
    time_from = models.DateTimeField(blank=True, null=True, default=None)
    time_to = models.DateTimeField(blank=True, null=True, default=None)
    is_week_start = models.BooleanField(default=False)
    is_day_start = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.date, self.time_from)

    class Meta:
        verbose_name = 'Calendar Item'
        verbose_name_plural = 'Calendar Items'


STATUSES = (
    ("booked", "booked"),
    ("available", "available"),
    ("unavailable", "unavailable"),
)


class CalendarItemStatus(models.Model):
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    booked = models.CharField(max_length=1, default=0)
    available = models.CharField(max_length=1, default=0)
    unavailable = models.CharField(max_length=1, default=0)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Calendar Item Status'
        verbose_name_plural = 'Calendar Item Statuses'


class CalendarItemGuide(models.Model):
    calendar_item = models.ForeignKey(CalendarItem)
    guide = models.ForeignKey(GuideProfile)
    order = models.ForeignKey("order.Order", blank=True, null=True, default=None)
    status = models.ForeignKey(CalendarItemStatus, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Guide Calendar Item'
        verbose_name_plural = 'Guide Calendar Items'


class ScheduleTemplateItem(models.Model):
    guide = models.ForeignKey(GuideProfile)
    day = models.IntegerField()
    hour = models.IntegerField()
    status = models.ForeignKey(CalendarItemStatus, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = 'Schedule Template Item'
        verbose_name_plural = 'Schedule Template Items'




