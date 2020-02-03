from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import json
from chats.models import Chat, ChatMessage
from django.contrib.auth.decorators import login_required
from orders.forms import GuideOrderAdjustForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django import forms


@login_required()
def livechat(request):
    current_page = "chat"
    return render(request, 'live_chat/index.html', locals())


@login_required()
def livechat_room(request, chat_uuid):
    current_page = "chat"
    user = request.user
    chat = Chat.objects.get(uuid=chat_uuid)
    if chat.guide != user and chat.tourist != user:
        messages.success(request, _('You do not have permissions to access this chat!'))
        return HttpResponseRedirect(reverse("home"))
    chat_messages = chat.chatmessage_set.all().values("chat_id", "message", "created", "user__username",
                                                      "user__generalprofile__first_name",
                                                      "user__generalprofile__id").order_by("created")

    order = chat.order
    # only dates for private tours or guide hourly booking can be adjusted
    if order and ((order.tour and order.tour.type == "2") or (not order.tour)):
        not_scheduled_tour = True
        form = GuideOrderAdjustForm(request.POST or None, instance=order)
        if request.method == "POST" and order.status.id in [1, 5]:  # pending or approved by guide
            if form.is_valid():  # payment reserved
                try:
                    form.save()
                except Exception as e:
                    messages.error(request, e)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'live_chat/room.html', locals())