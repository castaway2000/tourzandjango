from django.shortcuts import render
from .models import *

# Create your views here.


def chats(request):
    user = request.user
    chats = list(Chat.objects.all().values("guide__username", "tourist__username", "uuid", "id", "topic", "created"))
    chat_ids = [item["id"] for item in chats]
    chat_messages = ChatMessage.objects.filter(id__in=chat_ids).values("chat__id", "message", "created", "user__username").order_by("-created")

    touched_chat_ids = list()
    last_messages_dict = dict()
    for chat_message in chat_messages:
        if not chat_message["chat__id"] in touched_chat_ids:
            last_messages_dict[chat_message["chat__id"]] = {
                "text": chat_message["message"],
                "from": chat_message["user__username"],
                "created": chat_message["created"],
            }

    for chat in chats:
        chat["last_message"] = last_messages_dict.get(chat["id"])

    return render(request, 'chats/chats.html', locals())


def chat(request, uuid):
    user = request.user
    chat = Chat.objects.get(uuid=uuid)
    chat_messages = chat.chatmessage_set.all().values("chat_id", "message", "created", "user__username").order_by("created")
    return render(request, 'chats/chat.html', locals())