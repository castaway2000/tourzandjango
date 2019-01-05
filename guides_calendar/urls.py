from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^calendar/$', views.guide_calendar, name='guide_calendar'),
    url(r'^updating-calendar/$', views.updating_calendar, name='updating_calendar'),
    url(r'^weekly-schedule/$', views.weekly_schedule, name='weekly_schedule'),
    url(r'^updating-schedule-template/$', views.updating_schedule_template, name='updating_schedule_template'),
    url(r'^available-date-timeslots/$', views.available_date_timeslots, name='available_date_timeslots'),
]
