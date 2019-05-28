from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^guides/$', views.guides, name='guides'),
    # SEO purposes
    url(r'^local-tour-guide/$', views.guides, name='local_tour_guides'),
    url(r'^world-travel-guide/$', views.guides, name='world_travel_guide'),
    url(r'^private-tour-guide/$', views.guides, name='private_tour_guide'),
    url(r'^private-guide/$', views.guides, name='private_guide'),
    url(r'^travel-tour-guide/$', views.guides, name='travel_tour_guide'),
    url(r'^tour-guide/$', views.guides, name='tour_guide'),
    url(r'^get-your-guide/$', views.guides, name='get_your_guide'),
    url(r'^travel-guide/$', views.guides, name='travel_guide'),
    url(r'^local-expert/$', views.guides, name='tour_guide'),

    url(r'^guides/(?P<guide_name>.*)/(?P<general_profile_uuid>.*)/overview/$', views.guide, name='guide'),
    url(r'^guides/(?P<guide_name>.*)/(?P<general_profile_uuid>.*)/overview/(?P<new_view>\w+)/$', views.guide,
        name='guide_new'),

    url(r'^profile-settings/guide/$', views.profile_settings_guide, name='profile_settings_guide'),
    url(r'^profile-settings/guide-questions/$', views.profile_questions_guide, name='profile_questions_guide'),

    url(r'^search-guide/$', views.search_guide, name='search_guide'),
    url(r'^guide/registration/welcome/$', views.guide_registration_welcome, name='guide_registration_welcome'),

    #intermediate view to assign a session variable
    url(r'^guide/registration/welcome/confirmation$', views.guide_registration_welcome_confirmation,
        name='guide_registration_welcome_confirmation'),

    url(r'^guide/registration/$', views.profile_settings_guide, name='guide_registration'),
    url(r'^earnings/$', views.earnings, name='earnings'),
    url(r'^search-service/$', views.search_service, name='search_service'),

    url(r'^guide/payouts/$', views.guide_payouts, name='guide_payouts'),

    url(r'^guides-for-clients/$', views.guides_for_clients, name='guides_for_clients'),
    url(r'^tours-for-clients/$', views.tours_for_clients, name='tours_for_clients'),
    url(r'^ajax/rate_agregate/$', views.get_average_rate, name='get_average_rate'),

]
