from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^payment-methods/$', views.payment_methods, name='payment_methods'),
    url(r'^payment-methods-adding/$', views.payment_methods_adding, name='payment_methods_adding'),
    url(r'^payments/$', views.payments, name='payments'),
    url(r'^order-payment-checkout/(?P<order_uuid>\w+)/$', views.order_payment_checkout, name='order_payment_checkout'),
    url(r'^deleting-payment-method/(?P<payment_method_id>\w+)/$', views.deleting_payment_method, name='deleting_payment_method'),
    url(r'^payment-method-set-default/(?P<payment_method_id>\w+)/$', views.payment_method_set_default, name='payment_method_set_default'),
]