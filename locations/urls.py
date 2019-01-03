from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^search_city/$', views.search_city, name='search_city'),

    url(r'^all-countries/$', views.all_countries, name='all_countries'),
    url(r'^guides/(?P<country_slug>\S+)/(?P<city_slug>\S+)/$', views.location_guides, name='city_guides'),
    url(r'^guides/(?P<country_slug>\S+)/$', views.location_guides, name='country_guides'),

    url(r'^location-search-router/$', views.location_search_router, name='location_search_router'),
    url(r'^request-custom-booking/$', views.request_new_location_booking, name='request_new_location_booking'),
]
