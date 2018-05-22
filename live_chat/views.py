from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from chats.models import Chat, ChatMessage
from django.contrib.auth.decorators import login_required


@login_required()
def livechat(request):
    return render(request, 'live_chat/index.html', {})


@login_required()
def livechat_room(request, chat_uuid):
    chat_messages = ChatMessage.objects.filter(chat__uuid=chat_uuid)
    return render(request, 'live_chat/room.html', {
        "chat_messages": chat_messages,
        "chat_uuid": chat_uuid,
        "room_name_json": mark_safe(json.dumps(chat_uuid))
    })