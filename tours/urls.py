from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tours/$', views.tours, name='tours'),
    url(r'^tour/(?P<slug>[-\w]+)/$', views.tour, name='tour'),

    url(r'^settings/guide/tours/$', views.guide_settings_tours, name='guide_settings_tours'),
]
