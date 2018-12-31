import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import django
django.setup()

from twilio.rest import Client, TwilioException
from tourzan.settings import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE, USER_SMS_NMB_LIMIT,
    PHONE_SMS_NMB_LIMIT, DAILY_SMS_NMB_LIMIT,
)
from random import randint
from users.models import SmsSendingHistory
from datetime import datetime
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from notifications.models import Notification, NotificationSubject


class SendingSMS(object):
    current_site = Site.objects.get_current()
    domain = current_site.domain
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    from_phone = TWILIO_FROM_PHONE
    subject = None
    order = None
    chat = None

    def __init__(self, data=None):
        """
        getting phone_to is not anymore in class init method to be inline with the logic for emails, when one message can be sent
        both to guide and tourist
        """
        # if data:
        #     self.phone_to = data.get("phone_to")
        #     self.user_id = data.get("user_id")

    def get_info_from_order(self, order):
        guide_phone = order.guide.user.generalprofile.phone
        guide_user_id = order.guide.user.id
        tourist_phone = order.tourist.user.generalprofile.phone
        tourist_user_id = order.tourist.user.id
        return (guide_phone, guide_user_id, tourist_phone, tourist_user_id)

    def creating_random_string(self):
        random_string = randint(1000, 9999)
        self.random_string = random_string
        return random_string

    def send_validation_sms(self, phone_to, user_id):
        random_string = self.creating_random_string()
        message = "You verification code: %s" % random_string
        self.subject = "Verification"
        sms_sending_info = self.sending_sms(message, phone_to, user_id)
        return sms_sending_info

    def send_order_status_change_notification(self, order, status):
        if status.id == 1:
            if order.tour_scheduled:#scheduled tour, which means no approve from the guide
                message = "Congrats! You have received new order! Amount: %s USD, people: %s, date and time: %s" % \
                          ("%.2f" % order.total_price_before_fees, order.number_persons, order.tour_scheduled.dt.strftime("%m/%d/%Y at %H:%M"))
            else:
                message = "Congrats! You have received new order request! Amount: %s USD, people: %s, hours: %s, " \
                          "date and time: %s. " \
                          "Click the link below to confirm or to reject the order: %s%s" % \
                          ("%.2f" % order.total_price_before_fees, order.number_persons, order.hours_nmb,
                           order.date_booked_for.strftime("%m/%d/%Y at %H:%M"),
                           self.domain, reverse("livechat_room", kwargs={"chat_uuid": order.chat.uuid}))
            self.order = order
            self.subject = "New order"
        else:
            message = "Order status has been changed to %s! Click the link below to go to chat: %s%s" % \
                      (status.name, self.domain, reverse("livechat_room", kwargs={"chat_uuid": order.chat.uuid}))
            self.order = order
            self.subject = "Order status change"

        guide_phone, guide_user_id, tourist_phone, tourist_user_id = self.get_info_from_order(order)
        #sending to guide
        if guide_phone:
            self.sending_sms(message, phone_to=guide_phone, user_id=guide_user_id)

        #sending to tourist
        if tourist_phone:
            self.sending_sms(message, phone_to=tourist_phone, user_id=tourist_user_id)
        return True

    def send_new_message_notification(self, user_to, order=None, chat=None):
        message = "You have received new message from %s! Click the link below to see the details: %s%s" % \
                  (user_to.generalprofile.get_name(), self.domain, reverse("livechat_room", kwargs={"chat_uuid": order.chat.uuid}))
        self.order = order
        self.chat = chat
        self.subject = "Chat message notification"
        phone_to = user_to.generalprofile.phone
        if phone_to:
            self.sending_sms(message, phone_to=phone_to, user_id=user_to.id)
        return True

    def sending_sms(self, message, phone_to, user_id):
        today = datetime.today()
        sms_messages_user = SmsSendingHistory.objects.filter(user_id=user_id, created__date=today).count()
        sms_messages_phone = SmsSendingHistory.objects.filter(phone=phone_to, created__date=today).count()
        sms_messages_nmb_today = SmsSendingHistory.objects.filter(created__date=today).count()

        if len(phone_to) < 7:
            return {"status": "error", "message": "Phone number is too short!"}

        if self.subject == "Verification":
            if sms_messages_user > USER_SMS_NMB_LIMIT or sms_messages_phone > PHONE_SMS_NMB_LIMIT:
                return {"status": "error",
                        "message": "Your SMS limit was reached today. Please try again tomorrow or contact support!"}

        if sms_messages_nmb_today > DAILY_SMS_NMB_LIMIT:
            return {"status": "error", "message": "General SMS limit was reached. Please contact support!"}

        try:
            #Sending sms function which uses twilio

            self.client.messages.create(
                to=phone_to,
                from_=self.from_phone,
                body=message,
            )

            if self.subject == "Verification":
                SmsSendingHistory.objects.create(user_id=user_id, phone=phone_to, sms_code=self.random_string)
            elif self.subject:
                subject, created = NotificationSubject.objects.get_or_create(name=self.subject)
                kwargs = {
                    "subject": subject,
                    "phone": phone_to,
                    "user_id": user_id,
                }
                if self.order:
                    kwargs["order"] = self.order
                if self.chat:
                    kwargs["chat"] = self.chat
                Notification.objects.create(**kwargs)

            return {"status": "success", "message": "Sms was sent successfully!"}

        except TwilioException as exception:
            print(exception)
            return {"status": "error", "message": exception}
