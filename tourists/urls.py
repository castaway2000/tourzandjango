from django.conf.urls import url, include
from . import views

urlpatterns = [
    # url(r'^profile_overview/$', views.profile_overview, name='profile_overview'),
    # url(r'^profile_overview/(?P<username>\w+)/$', views.profile_overview, name='profile_overview'),
    # url(r'^profile_photos/$', views.profile_photos, name='profile_photos'),
    # url(r'^profile_photos/(?P<username>\w+)/$', views.profile_photos, name='profile_photos'),

    url(r'^profile_settings/tourist/$', views.profile_settings_tourist, name='profile_settings_tourist'),
    url(r'^tourists/(?P<username>\w+)/overview/$', views.tourist, name='tourist'),

]
