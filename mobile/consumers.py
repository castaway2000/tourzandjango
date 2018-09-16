from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from mobile.models import GeoChat, GeoChatMessage
import datetime
from django.core.cache import cache
from tourzan.settings import USER_LASTSEEN_TIMEOUT


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"] #user object
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        chat_uuid = text_data_json.get("chat_uuid")

        #update last user activity dt - the same as in users.middleware.TrackingActiveUserMiddleware
        self.update_last_user_activity_dt()

        #saving message to the database
        message_user, dt = self.save_message_to_db(message, chat_uuid)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": message_user,
                "dt": dt
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event.get('message')
        user = event.get("user")
        dt = event.get("dt")

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "message": message,
            "user": user,
            "dt": dt
        }))

    def save_message_to_db(self, message, chat_uuid):
        user = self.user
        chat = GeoChat.objects.get(uuid=chat_uuid)
        if chat.guide == user or chat.tourist == user:
            chat_message = GeoChatMessage.objects.create(chat=chat, message=message, user=user)
            message_user = user.generalprofile.first_name if hasattr(user, "generalprofile") and user.generalprofile.first_name != "" else user.username
            dt = chat_message.created.strftime("%m/%d/%Y %H:%M:%S")
            return (message_user, dt)

    def update_last_user_activity_dt(self):
        user = self.user
        if user.is_authenticated():
            now = datetime.datetime.now()
            cache.set('seen_%s' % (user.id), now, USER_LASTSEEN_TIMEOUT)