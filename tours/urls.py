from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tours/$', views.tours, name='tours'),

    url(r'^tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.tour, name='tour'),
    url(r'^tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/(?P<tour_new>\w+)/$', views.tour, name='tour_new'),


    url(r'^settings/guide/tours/$', views.guide_settings_tours, name='guide_settings_tours'),
    url(r'^settings/guide/tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.guide_settings_tour_edit, name='guide_settings_tour_edit'),

    url(r'^settings/guide/tour_create/$', views.guide_settings_tour_edit_general, name='guide_settings_tour_create'),

    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/general/$',
        views.guide_settings_tour_edit_general, name='tour_edit_general'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/program/$',
        views.guide_settings_tour_edit_program, name='tour_edit_program'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/images/$', views.guide_settings_tour_edit_images, name='tour_edit_images'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/price-and-schedule/$', views.guide_settings_tour_edit_price_and_schedule,
        name='tour_edit_price_and_schedule'),

    url(r'^settings/guide/tour-new/delete_program_tour_item/(?P<id>\w+)/$',
        views.delete_program_tour_item, name='delete_program_tour_item'),

    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/available-tour-dates-template/$',
        views.available_tour_dates_template, name='available_tour_dates_template'),


    url(r'^deactivate_tour_image/$', views.deactivate_tour_image, name='deactivate_tour_image'),
    url(r'^make_main_tour_image/$', views.make_main_tour_image, name='make_main_tour_image'),

    url(r'^tour_deleting/(?P<tour_id>\w+)/$', views.tour_deleting, name='tour_deleting'),

]
