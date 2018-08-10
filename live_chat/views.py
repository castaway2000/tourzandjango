from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import json
from chats.models import Chat, ChatMessage
from django.contrib.auth.decorators import login_required
from orders.forms import GuideOrderAdjustForm
from django.contrib import messages
from django.utils.translation import ugettext as _


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
        messages.success(request, _('You have no permissions to access this chat!'))
        return HttpResponseRedirect(reverse("home"))
    chat_messages = chat.chatmessage_set.all().values("chat_id", "message", "created", "user__username",
                                                      "user__generalprofile__first_name").order_by("created")

    order = chat.order
    if order and ((order.tour and order.tour.type=="2") or (not order.tour)):#only dates for private tours or guide hourly booking can be adjusted
        form = GuideOrderAdjustForm(request.POST or None, instance=order)
        if request.method == "POST" and order.status.id == 1:#pending
            if form.is_valid() and not order.is_approved_by_guide:
                new_form = form.save(commit=False)
                new_form.save()
                if order.guide.user == user and request.session.get("current_role") == "guide":
                    order.is_approved_by_guide = True
                    order.save(force_update=True)

            elif order.tourist.user == user and request.session.get("current_role") != "guide":
                if "approve" in request.POST:
                    return HttpResponseRedirect(reverse("order_payment_checkout", kwargs={"order_uuid": order.uuid}))
                elif "edit_details" in request.POST:
                    order.is_approved_by_guide = False
                    order.save(force_update=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'live_chat/room.html', locals())