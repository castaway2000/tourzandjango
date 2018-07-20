from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
from .models import *
from tours.models import Tour
from guides.models import GuideProfile
from django.contrib.auth.decorators import login_required
from tourzan.settings import GOOGLE_RECAPTCHA_SECRET_KEY
from django.contrib import messages

import requests



@login_required()
def chats(request):
    user = request.user
    chats = list(Chat.objects.filter(Q(guide=user)|Q(tourist=user))
                 .values("guide__generalprofile__first_name", "tourist__generalprofile__first_name",
                         "guide__generalprofile__uuid",
                         "tourist__generalprofile__uuid",
                         "tourist__username", "guide__username",
                         "uuid", "id", "topic", "created"))

    chat_ids = [item["id"] for item in chats]

    chat_messages = ChatMessage.objects.filter(chat_id__in=chat_ids).values("chat__id", "message", "created",
                                                                            "user__generalprofile__first_name",
                                                                            "user__username").order_by("id")

    touched_chat_ids = list()
    last_messages_dict = dict()
    for chat_message in chat_messages:
        if not chat_message["chat__id"] in touched_chat_ids:
            last_messages_dict[chat_message["chat__id"]] = {
                "text": chat_message["message"],
                "from": chat_message["user__generalprofile__first_name"],
                "created": chat_message["created"],
            }

    for chat in chats:
        chat["last_message"] = last_messages_dict.get(chat["id"])
        chat["last_message_dt"] = last_messages_dict[chat["id"]]["created"] if last_messages_dict.get(chat["id"]) else None

    return render(request, 'chats/chats.html', locals())


@login_required()
def chat(request, uuid):
    user = request.user
    chat = Chat.objects.get(uuid=uuid)
    if chat.guide != user and chat.tourist != user:
        return HttpResponseRedirect(reverse("home"))

    chat_messages = chat.chatmessage_set.all().values("chat_id", "message", "created", "user__username",
                                                      "user__generalprofile__first_name").order_by("created")
    return render(request, 'chats/chat.html', locals())


@login_required()
def sending_chat_message(request):
    user = request.user
    return_data = dict()
    data = request.POST
    message = data.get("message")
    chat_uuid = data.get("chat_uuid")
    # google captcha validatings
    recaptcha_response = request.POST.get('g-recaptcha-response')
    if recaptcha_response and recaptcha_response != "":
        data = {
            'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        if result['success']:
            if message and chat_uuid:
                chat = Chat.objects.get(uuid=chat_uuid)
                if chat.guide == user or chat.tourist == user:
                    chat_message = ChatMessage.objects.create(chat=chat, message=message, user=user)
                    return_data["message"] = message
                    return_data["author"] = "me"
                    return_data["created"] = datetime.strftime(chat_message.created, "%m.%d.%Y %H:%M:%S")
            return JsonResponse(return_data)


@login_required()
def chat_creation(request, tour_id=None, guide_uuid=None, order_uuid=None):
    user = request.user

    if tour_id:
        tour = Tour.objects.get(id=tour_id)
        guide_user = tour.guide.user
        topic = "Query about the tour %s" % tour.name
        chat, created = Chat.objects.get_or_create(tour_id=tour_id, tourist=user,
                                                   defaults={"guide": guide_user,
                                                             "topic": topic})
    elif guide_uuid:
        guide = GuideProfile.objects.get(uuid=guide_uuid)
        topic = "Chat with %s" % guide.user.generalprofile.first_name
        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user, defaults={"topic": topic})

    elif order_uuid:
        order = Order.objects.get(uuid=order_uuid)
        guide = order.guide
        topic = "Chat with %s" % guide.user.generalprofile.first_name
        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user, order=order,
                                                   defaults={"topic": topic})


    return HttpResponseRedirect(reverse("livechat_room", kwargs={"chat_uuid": chat.uuid} ))
