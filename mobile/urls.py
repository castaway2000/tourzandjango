from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^mobile/waitlist/$', views.waitlist, name='waitlist'),
]
