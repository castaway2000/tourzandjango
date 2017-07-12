from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^blog/$', views.blog, name='blog'),
    url(r'^blog_post/(?P<slug>\S+)/$', views.blog_post, name='blog_post'),
]
