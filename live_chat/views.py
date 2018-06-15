from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import json
from chats.models import Chat, ChatMessage
from django.contrib.auth.decorators import login_required


@login_required()
def livechat(request):
    return render(request, 'live_chat/index.html', {})


@login_required()
def livechat_room(request, chat_uuid):
    user = request.user
    chat = Chat.objects.get(uuid=chat_uuid)
    if chat.guide != user and chat.tourist != user:
        return HttpResponseRedirect(reverse("home"))
    chat_messages = chat.chatmessage_set.all().values("chat_id", "message", "created", "user__username",
                                                      "user__generalprofile__first_name").order_by("created")
    return render(request, 'live_chat/room.html', {
        "chat": chat,
        "chat_messages": chat_messages,
        "chat_uuid": chat_uuid,
        "room_name_json": mark_safe(json.dumps(chat_uuid))
    })