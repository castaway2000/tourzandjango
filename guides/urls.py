from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^guides/$', views.guides, name='guides'),
    url(r'^guides/(?P<username>\w+)/overview/$', views.guide, name='guide'),

    url(r'^profile_settings/guide/$', views.profile_settings_guide, name='profile_settings_guide'),
    url(r'^search_guide/$', views.search_guide, name='search_guide'),

    url(r'^guide/registration/welcome/$', views.guide_registration_welcome, name='guide_registration_welcome'),
    url(r'^guide/registration/$', views.guide_registration, name='guide_registration'),

    url(r'^earnings/$', views.earnings, name='earnings'),

]
