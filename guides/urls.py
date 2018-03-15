from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^guides/$', views.guides, name='guides'),
    url(r'^guides/(?P<guide_name>\w+)/(?P<general_profile_uuid>.*)/overview/$', views.guide, name='guide'),
    url(r'^guides/(?P<guide_name>\w+)/(?P<general_profile_uuid>.*)/overview/(?P<new_view>\w+)/$', views.guide, name='guide_new'),

    url(r'^profile_settings/guide/$', views.profile_settings_guide, name='profile_settings_guide'),
    url(r'^search_guide/$', views.search_guide, name='search_guide'),
    url(r'^guide/registration/welcome/$', views.guide_registration_welcome, name='guide_registration_welcome'),

    #intermediate view to assign a session variable
    url(r'^guide/registration/welcome/confirmation$', views.guide_registration_welcome_confirmation,
        name='guide_registration_welcome_confirmation'),

    url(r'^guide/registration/$', views.profile_settings_guide, name='guide_registration'),
    url(r'^earnings/$', views.earnings, name='earnings'),
    url(r'^search_service/$', views.search_service, name='search_service'),

    url(r'^guide/payouts/$', views.guide_payouts, name='guide_payouts'),

    url(r'^guides_for_clients/$', views.guides_for_clients, name='guides_for_clients'),
    url(r'^tours_for_clients/$', views.tours_for_clients, name='tours_for_clients'),

]
