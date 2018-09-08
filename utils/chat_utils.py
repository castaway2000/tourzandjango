from chats.models import Chat
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import datetime
from django.contrib.auth.models import User

class ChatHelper():
    layer = get_channel_layer()
    tourzan_user_name = "Tourzan bot"
    tourzan_user, created = User.objects.get_or_create(username=tourzan_user_name)

    def send_order_message_and_notification(self, chat, message):
        chat.create_message(self.tourzan_user, message)
        self.send_order_message(chat, message)
        # send message to general websockets
        uuids = [chat.guide.generalprofile.uuid, chat.tourist.generalprofile.uuid]
        for uuid in uuids:
            self.send_notification(chat, message, uuid)

    def send_order_message(self, chat, message):
        # send message to chat websockets
        room_group = 'chat_%s' % chat.uuid
        async_to_sync(self.layer.group_send)(
            room_group,
            {
                "type": "chat_message",
                "message": message,
                "user": self.tourzan_user_name,
                "dt": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                "message_type": "system",
            }
        )

    def send_notification(self, chat, message, uuid):
        async_to_sync(self.layer.group_send)(
            uuid,
            {
                'type': 'chat_notification',
                'message': message,
                'message_user_name': self.tourzan_user_name,
                'chat_uuid': str(chat.uuid),
                'color_type': 'info',
                'notification_type': 'order_status_change'
            }
        )