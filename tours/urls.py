from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tours/$', views.tours, name='tours'),
    url(r'^tour/(?P<slug>[-\w]+)/$', views.tour, name='tour'),

]
