from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^coupon_validation/', views.coupon_validation, name='coupon_validation'),
]