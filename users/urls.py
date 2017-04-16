from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),

    url(r'^guides/(?P<username>\w+)/overview/$', views.guide, name='guide'),

    url(r'^profile_settings/$', views.profile_settings, name='profile_settings'),
    url(r'^profile_settings/guide/$', views.profile_settings_guide, name='profile_settings_guide'),
    url(r'^profile_settings/tourist/$', views.profile_settings_tourist, name='profile_settings_tourist'),

    url(r'^general_settings/$', views.general_settings, name='general_settings'),

    url(r'^profile_overview/$', views.profile_overview, name='profile_overview'),
    url(r'^profile_overview/(?P<username>\w+)/$', views.profile_overview, name='profile_overview'),
    url(r'^profile_photos/$', views.profile_photos, name='profile_photos'),
    url(r'^profile_photos/(?P<username>\w+)/$', views.profile_photos, name='profile_photos'),

    url(r'^set_language/(?P<language>\w+)/$', views.set_language, name='set_language'),
]
