from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^curated-tours-a/$', views.curated_tours_a, name='curated_tours_a'),
    url(r'^curated-tours-b/$', views.curated_tours_b, name='curated_tours_b'),
    url(r'^curated-tours-c/$', views.curated_tours_c, name='curated_tours_c'),

    url(r'^curated-tours-results/$', views.curated_tours_results, name='curated_tours_results'),

    url(r'^tours/$', views.tours, name='tours'),

    # SEO purposes
    url(r'^tours-by-locals/$', views.tours, name='tours_by_locals'),
    url(r'^affordable-tours/$', views.tours, name='affordable_tours'),
    url(r'^toursbylocals/$', views.tours, name='toursbylocals'),
    url(r'^tour-companies/$', views.tours, name='tour_companies'),
    url(r'^guided-travel-tours/$', views.tours, name='guided_travel_tours'),

    # url(r'^tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.tour, name='tour'),
    url(r'^tour/(?P<slug>[-\w]+)/(?P<tour_uuid>\w+)/(?P<tour_new>\w+)/$', views.tour, name='tour_new'),


    url(r'^settings/guide/tours/$', views.guide_settings_tours, name='guide_settings_tours'),
    url(r'^settings/guide/tour/(?P<slug>[-\w]+)/(?P<tour_id>\w+)/$', views.guide_settings_tour_edit,
        name='guide_settings_tour_edit'),

    url(r'^settings/guide/tour-create/$', views.guide_settings_tour_edit_general, name='guide_settings_tour_create'),

    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/general/$',
        views.guide_settings_tour_edit_general, name='tour_edit_general'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/program/$',
        views.guide_settings_tour_edit_program, name='tour_edit_program'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/images/$', views.guide_settings_tour_edit_images, name='tour_edit_images'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/price-and-schedule/$', views.guide_settings_tour_edit_price_and_schedule,
        name='tour_edit_price_and_schedule'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/(?P<uuid>[-\w]+)/scheduled-tour/$', views.tour_edit_scheduled_tour,
        name='tour_edit_scheduled_tour'),
    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/price/$', views.tour_edit_price,
        name='tour_edit_price'),

    url(r'^settings/guide/tour-new/manage-weekly-template-item/$',
        views.manage_weekly_template_item, name='manage_weekly_template_item'),

    url(r'^settings/guide/tour-new/apply-week-template-to-dates/(?P<slug>[-\w]+)/$',
        views.apply_week_template_to_dates, name='apply_week_template_to_dates'),

    url(r'^settings/guide/tour-new/delete_program_tour_item/(?P<id>\w+)/$',
        views.delete_program_tour_item, name='delete_program_tour_item'),

    url(r'^settings/guide/tour-new/(?P<slug>[-\w]+)/available-tour-dates-template/$',
        views.available_tour_dates_template, name='available_tour_dates_template'),

    url(r'^settings/guide/tour-new/(?P<uuid>[-\w]+)/scheduled-tour-delete/$',
        views.scheduled_tour_delete, name='scheduled_tour_delete'),


    url(r'^deactivate_tour_image/$', views.deactivate_tour_image, name='deactivate_tour_image'),
    url(r'^make_main_tour_image/$', views.make_main_tour_image, name='make_main_tour_image'),

    url(r'^tour_deleting/(?P<tour_id>\w+)/$', views.tour_deleting, name='tour_deleting'),

]
