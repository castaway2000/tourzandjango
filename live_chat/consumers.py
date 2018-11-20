from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from chats.models import Chat, ChatMessage
import datetime
from django.core.cache import cache
from tourzan.settings import USER_LASTSEEN_TIMEOUT
from channels.layers import get_channel_layer
from django.utils.text import Truncator
import logging
l = logging.getLogger(__name__)
from emoticons.templatetags.emoticons_tags import regexp_replace_emoticons


class GeneralConsumer(WebsocketConsumer):
    def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        l.debug("connect general")
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            self.close()
            # await self.accept()
        else:
            self.group_name = self.scope['user'].generalprofile.uuid

            # Join group
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )

            # Send debug message for testing
            # async_to_sync(self.channel_layer.group_send)(
            #     self.group_name,
            #     {
            #         "type": "chat_message_test",
            #         "message": "test 12345",
            #     }
            # )

            self.accept()

    def chat_message_test(self, event):
        # Handles the "chat.message" event when it's sent to us.
        l.debug("debugging chat message")
        l.debug(event)
        try:
            self.send(text_data=json.dumps({
                "message": "hello there 12345",
            }))
        except Exception as e:
            l.debug(e)

    def chat_notification(self, event):
        """
        Send notification to user about new chat message
        """
        l.debug("chat_notification")
        message = Truncator(event["message"]).chars(75)
        message_user_name = event["message_user_name"]
        chat_uuid = event["chat_uuid"]
        color_type = event["color_type"]
        notification_type = event["notification_type"] if "notification_type" in event else "new_chat_message_notification"
        try:
            l.debug("try")
            self.send(text_data=json.dumps({
                "type": notification_type,
                "message": message,
                "message_user_name": message_user_name,
                #It is needed for showing or not showing notification about the message
                #(comparing with uuid in the current url)
                "chat_uuid": chat_uuid,
                "color_type": color_type,
            }))
        except Exception as e:
            l.debug(e)


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        l.debug("connect sockets")
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
        chat, message_user_name, message_to_user_obj, dt, user_id = self.save_message_to_db(message, chat_uuid)
        # Send message to room group
        l.debug("sending message to chat")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": message_user_name,
                "user_id": user_id,
                "dt": dt
            }
        )
        print(user_id)

        #Notification to general websockets
        uuid = message_to_user_obj.generalprofile.uuid
        async_to_sync(self.channel_layer.group_send)(
            uuid,
            {
                'type': 'chat.notification',
                'message': message,
                'message_user_name': message_user_name,
                'chat_uuid': chat_uuid,
                'user_id': user_id,
                "color_type": "success"
            }
        )


    def chat_message(self, event):
        """
        Called when someone sent message to chat.
        """
        l.debug("chat message of chat consumer")
        message = event.get('message')
        message_with_emoticons = regexp_replace_emoticons(message)

        user = event.get("user")
        dt = event.get("dt")
        message_type = event.get("message_type", "None")
        user_id = event.get('user_id')
        # Send message to chat webSocket
        self.send(text_data=json.dumps({
            "message": message_with_emoticons,
            "user": user,
            "user_id": user_id,
            "dt": dt,
            "message_type": message_type
        }))

    def save_message_to_db(self, message, chat_uuid):
        user = self.user
        chat = Chat.objects.get(uuid=chat_uuid)
        if chat.guide == user or chat.tourist == user:
            message_to_user_obj = chat.tourist if chat.guide == user else chat.guide #defining user to whom message was sent in chat
            chat_message = ChatMessage.objects.create(chat=chat, message=message, user=user)
            message_user = user.generalprofile.get_name() if hasattr(user, "generalprofile") else user.username
            dt = chat_message.created.strftime("%m/%d/%Y %H:%M:%S")
            return (chat, message_user, message_to_user_obj, dt, user.generalprofile.user_id)

    def update_last_user_activity_dt(self):
        user = self.user
        if user.is_authenticated():
            now = datetime.datetime.now()
            cache.set('seen_%s' % (user.id), now, USER_LASTSEEN_TIMEOUT)