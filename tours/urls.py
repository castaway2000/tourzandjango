from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tours/$', views.tours, name='tours'),

    url(r'^guides/(?P<username>\w+)/tours/$', views.guide_tours, name='guide_tours'),
]
