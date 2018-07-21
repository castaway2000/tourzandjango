from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^making_booking/$', views.making_booking, name='making_booking'),

    url(r'^bookings/$', views.bookings, name='my_bookings'),
    url(r'^bookings/(?P<status>\S+)/$', views.bookings, name='my_bookings_status'),

    url(r'^orders/$', views.orders, name='orders'),
    url(r'^orders/(?P<status>\S+)/$', views.orders, name='orders_status'),

    url(r'^settings/guide/orders/$', views.guide_settings_orders, name='guide_settings_orders'),
    url(r'^settings/tourist/orders/$', views.tourist_settings_orders, name='tourist_settings_orders'),

    url(r'^cancel_order/(?P<order_uuid>\w+)/$', views.cancel_order, name='cancel_order'),
    url(r'^change_order_status/(?P<order_id>\w+)/(?P<status_id>\w+)/$', views.change_order_status,
        name='change_order_status'),

    url(r'^saving_review/$', views.saving_review, name='saving_review'),

    url(r'^order_completing_page/(?P<order_id>\w+)/$', views.order_completing, name='order_completing'),
]
