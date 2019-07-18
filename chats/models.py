from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour
from orders.models import Order
import uuid
from utils.sending_emails import SendingEmail
from django.db.models.signals import post_save
from utils.disabling_signals_for_load_data import disable_for_loaddata
from notifications.models import Notification
import datetime
from django.utils import timezone


class Chat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    guide = models.ForeignKey(User, related_name="guide")
    tourist = models.ForeignKey(User, related_name="tourist")
    order = models.OneToOneField(Order, blank=True, null=True, default=None)
    tour = models.ForeignKey(Tour, blank=True, null=True, default=None)#a chat converstion can be around some specific tour
    topic = models.CharField(max_length=256, blank=True, null=True, default=None)#some topic can be specified as well
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s-%s" % (self.guide.generalprofile.first_name, self.tourist.generalprofile.first_name)

    def create_message(self, user, message, is_automatic=False):
        ChatMessage.objects.create(chat=self, message=message, user=user, is_automatic=is_automatic)
        return True

    @property
    def last_chat_message_dt(self):
        last_chat_message = self.chatmessage_set.all().last()
        if last_chat_message:
            return last_chat_message.created
        else:
            return 1


class ChatMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat)
    message = models.TextField()
    user = models.ForeignKey(User)
    is_automatic = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s: %s" % (self.chat.created, self.user.username)


    def save(self, *args, **kwargs):
        super(ChatMessage, self).save(*args, **kwargs)

    def get_receiver_user(self):
        current_user = self.user
        chat = self.chat
        if current_user:
            receiver_user = chat.tourist if chat.tourist != current_user else chat.guide
        else:
            receiver_user = None
        return receiver_user


@disable_for_loaddata
def chat_message_post_save(sender, instance, created, **kwargs):
    receiver_user = instance.get_receiver_user()

    chat = instance.chat
    now = timezone.now()
    print(now)
    last_message = ChatMessage.objects.filter(chat=chat).exclude(id=instance.id).first()
    timeout_seconds = 60 * 1  # 5 minutes

    # if last_message:
    #     print(last_message.created)
    #     print(now > last_message.created + datetime.timedelta(seconds=timeout_seconds))

    if not last_message or (now > last_message.created + datetime.timedelta(seconds=timeout_seconds)):
        if receiver_user and not receiver_user.generalprofile.get_is_user_online() and not instance.is_automatic:
            data = {"chat_message": instance, "user_from": instance.user, "user_to": receiver_user}
            SendingEmail(data).send_new_message_email()

            order = instance.chat.order
            from utils.sending_sms import SendingSMS
            sms = SendingSMS()
            sms.send_new_message_notification(user_to=receiver_user, order=order, chat=chat)

post_save.connect(chat_message_post_save, sender=ChatMessage)


