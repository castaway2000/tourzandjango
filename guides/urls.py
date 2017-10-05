from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^guides/$', views.guides, name='guides'),
    url(r'^guides/(?P<username>\w+)/overview/$', views.guide, name='guide'),
    url(r'^profile_settings/guide/$', views.profile_settings_guide, name='profile_settings_guide'),
    url(r'^search_guide/$', views.search_guide, name='search_guide'),
    url(r'^guide/registration/welcome/$', views.guide_registration_welcome, name='guide_registration_welcome'),
    url(r'^guide/registration/$', views.profile_settings_guide, name='guide_registration'),
    url(r'^earnings/$', views.earnings, name='earnings'),
    url(r'^search_service/$', views.search_service, name='search_service'),

    url(r'^guide/payouts/$', views.guide_payouts, name='guide_payouts'),

    url(r'^guides_for_clients/$', views.guides_for_clients, name='guides_for_clients'),
    url(r'^tours_for_clients/$', views.tours_for_clients, name='tours_for_clients'),

]
