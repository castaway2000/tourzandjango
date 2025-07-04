from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^blog/$', views.blog, name='blog'),
    url(r'^blog/category/(?P<category_slug>\S+)/$', views.blog, name='blog_category_slug'),
    url(r'^blog/(?P<slug>\S+)/$', views.blog_post, name='blog_post'),
]
