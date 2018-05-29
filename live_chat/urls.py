from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^live-chat/$', views.livechat, name='livechat'),
    url(r'^live-chat/(?P<chat_uuid>[^/]+)/$', views.livechat_room, name='livechat_room'),
]