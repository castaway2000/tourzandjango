from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/application/$', views.api_partner_application, name='api_partner_application'),
    url(r'^api/application/success/$', views.api_partner_application_success, name='api_partner_application_success'),
]
