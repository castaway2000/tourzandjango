from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^search_city/$', views.search_city, name='search_city'),

    url(r'^all-countries/$', views.all_countries, name='all_countries'),
    url(r'^guides/in/(?P<country_slug>\S+)/(?P<city_slug>\S+)/$', views.location_guides, name='city_guides'),
    url(r'^guides/in/(?P<country_slug>\S+)/$', views.location_guides, name='country_guides'),

    # SEO reasons
    url(r'^(?P<country_slug>\S+)-tourism/$', views.country_city_guides, name='country_guides'),
    url(r'^visit-(?P<country_slug>\S+)/$', views.country_city_guides, name='country_guides'),
    url(r'^(?P<country_slug>\S+)-travel-guide/$', views.country_city_guides, name='country_guides'),
    url(r'^(?P<country_slug>\S+)-guided-tours/$', views.country_city_guides, name='country_guides'),
    url(r'^guided-tours-of-(?P<country_slug>\S+)/$', views.country_city_guides, name='country_guides'),
    url(r'^private-tours-of-(?P<country_slug>\S+)/$', views.country_city_guides, name='country_guides'),
    url(r'^(?P<country_slug>\S+)-tours/$', views.country_city_guides, name='country_guides'),

    url(r'^machu-picchu-tours/$', views.machu_picchu, name='machu_picchu'),
    url(r'^location-search-router/$', views.location_search_router, name='location_search_router'),
    url(r'^request-custom-booking/$', views.request_new_location_booking, name='request_new_location_booking'),
]
