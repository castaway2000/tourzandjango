from django.conf.urls import url, include
from . import views

urlpatterns = [
    # url(r'^profile_overview/$', views.profile_overview, name='profile_overview'),
    # url(r'^profile_overview/(?P<username>\w+)/$', views.profile_overview, name='profile_overview'),
    # url(r'^profile_photos/$', views.profile_photos, name='profile_photos'),
    # url(r'^profile_photos/(?P<username>\w+)/$', views.profile_photos, name='profile_photos'),

    url(r'^profile-settings/tourist/$', views.profile_settings_tourist, name='profile_settings_tourist'),


    url(r'^profile-settings/travel-photos/$', views.travel_photos, name='travel_photos'),
    url(r'^profile-settings/deleting-travel-photo/(?P<photo_id>\w+)/$', views.deleting_travel_photo,
        name='deleting_travel_photo'),

    url(r'^tourists/(?P<uuid>\S+)/overview/$', views.tourist, name='tourist'),

]
