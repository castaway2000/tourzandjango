from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tour_booking/$', views.tour_booking, name='tour_booking'),
    url(r'^bookings/$', views.bookings, name='my_bookings'),
    url(r'^bookings/(?P<status>\S+)/$', views.bookings, name='my_bookings_status'),

    url(r'^orders/$', views.orders, name='orders'),
    url(r'^orders/(?P<status>\S+)/$', views.orders, name='orders_status'),
]
