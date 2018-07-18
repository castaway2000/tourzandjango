from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^chats/$', views.chats, name='chats'),

    url(r'^chats/chat_uuid/(?P<uuid>\S+)/$', views.chat, name='chat'),

    url(r'^sending_chat_messages/$', views.sending_chat_message, name='sending_chat_message'),

    url(r'^chat_creation/tour/(?P<tour_id>\S+)/$', views.chat_creation, name='chat_creation_tour'),
    url(r'^chat_creation/guide/(?P<guide_uuid>\S+)/$', views.chat_creation, name='chat_creation_guide'),
]
