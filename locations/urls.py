from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^search_city/$', views.search_city, name='search_city'),

]
