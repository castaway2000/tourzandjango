from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^calendar/$', views.guide_calendar, name='guide_calendar'),
    url(r'^updating_calendar/$', views.updating_calendar, name='updating_calendar'),
    url(r'^weekly_schedule/$', views.weekly_schedule, name='weekly_schedule'),
    url(r'^updating_schedule_template/$', views.updating_schedule_template, name='updating_schedule_template'),
]
