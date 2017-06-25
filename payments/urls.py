from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^payment_methods/$', views.payment_methods, name='payment_methods'),
    url(r'^payment_methods_adding/$', views.payment_methods_adding, name='payment_methods_adding'),
    url(r'^making_order_payment/(?P<order_id>\w+)/$', views.making_order_payment, name='making_order_payment'),

    url(r'^payments/$', views.payments, name='payments'),
    url(r'^order_payment_checkout/(?P<order_id>\w+)/$', views.order_payment_checkout, name='order_payment_checkout'),
]