from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tours/$', views.tours, name='tours'),

    url(r'^tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.tour, name='tour'),


    url(r'^settings/guide/tours/$', views.guide_settings_tours, name='guide_settings_tours'),
    url(r'^settings/guide/tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.guide_settings_tour_edit, name='guide_settings_tour_edit'),
    url(r'^settings/guide/tour_create/$', views.guide_settings_tour_edit, name='guide_settings_tour_create'),


    url(r'^deactivate_tour_image/$', views.deactivate_tour_image, name='deactivate_tour_image'),

]
