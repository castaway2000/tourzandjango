from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from chats.models import Chat, ChatMessage
import datetime
from django.core.cache import cache
from tourzan.settings import USER_LASTSEEN_TIMEOUT
from channels.layers import get_channel_layer
from django.utils.text import Truncator


class GeneralConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
            # await self.accept()
        else:
            # Accept the connection
            await self.accept()

        self.group_name = self.scope['user'].generalprofile.uuid

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Send debug message for testing
        # await self.channel_layer.group_send(
        #     self.group_name,
        #     {
        #         "type": "chat.message",
        #         "message": "test 12345",
        #     }
        # )

    async def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        try:
            await self.send_json({
                "message": "hello there 1234",
            })
        except Exception as e:
            print(e)


    async def chat_notification(self, event):
        """
        Send notification to user about new chat message
        """
        message =  Truncator(event["message"]).chars(75)
        message_user_name = event["message_user_name"]
        chat_uuid = event["chat_uuid"]
        color_type = event["color_type"]
        try:
            await self.send_json({
                "type": "new_chat_message_notification",
                "message": message,
                "message_user_name": message_user_name,
                "chat_uuid": chat_uuid,
                "color_type": color_type
            })
        except Exception as e:
            print(e)


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
        chat, message_user_name, message_to_user_obj, dt = self.save_message_to_db(message, chat_uuid)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": message_user_name,
                "dt": dt
            }
        )

        #Notification to general websockets
        uuid = message_to_user_obj.generalprofile.uuid
        async_to_sync(self.channel_layer.group_send)(
            uuid,
            {
                'type': 'chat.notification',
                'message': message,
                'message_user_name': message_user_name,
                'chat_uuid': chat_uuid,
                "color_type": "success"
            }
        )


    def chat_message(self, event):
        """
        Called when someone sent message to chat.
        """
        message = event.get('message')
        user = event.get("user")
        dt = event.get("dt")
        message_type = event.get("message_type", "None")

        # Send message to chat webSocket
        self.send(text_data=json.dumps({
            "message": message,
            "user": user,
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
            return (chat, message_user, message_to_user_obj, dt)

    def update_last_user_activity_dt(self):
        user = self.user
        if user.is_authenticated():
            now = datetime.datetime.now()
            cache.set('seen_%s' % (user.id), now, USER_LASTSEEN_TIMEOUT)