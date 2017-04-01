from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^chats/$', views.chats, name='chats'),
    url(r'^chats/(?P<uuid>\S+)/$', views.chat, name='chat'),
]
