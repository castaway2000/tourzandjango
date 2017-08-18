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


class SendingSMS(object):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    from_phone = TWILIO_FROM_PHONE

    def __init__(self, data):
        phone_to = data.get("phone_to")
        self.phone_to = phone_to
        self.user_id = data.get("user_id")


    def creating_random_string(self):
        random_string = randint(1000, 9999)
        self.random_string = random_string
        return random_string


    def send_validation_sms(self):
        random_string = self.creating_random_string()
        message = "You verification code: %s" % random_string
        sms_sending_info = self.sending_sms(message)
        return sms_sending_info


    def sending_sms(self, message):
        user_id = self.user_id
        phone_to = self.phone_to
        # print ('entered to sms send')

        today = datetime.today()
        sms_messages_user = SmsSendingHistory.objects.filter(user_id=user_id, created__date=today).count()
        sms_messages_phone = SmsSendingHistory.objects.filter(phone=phone_to, created__date=today).count()
        sms_messages_nmb_today = SmsSendingHistory.objects.filter(created__date=today).count()

        if len(phone_to) < 7:
            return {"status": "error", "message": "Phone number is too short!"}
        elif sms_messages_user > USER_SMS_NMB_LIMIT or sms_messages_phone > PHONE_SMS_NMB_LIMIT:
            return {"status": "error", "message": "Your SMS limit was reached today. Please try again tomorrow or contact support!"}
        elif sms_messages_nmb_today > DAILY_SMS_NMB_LIMIT:
            return {"status": "error", "message": "General SMS limit was reached. Please contact support!"}
        else:
            try:
                #Sending sms function which uses twilio
                # self.client.messages.create(
                #     to=phone_to,
                #     from_=self.from_phone,
                #     body=message,
                # )

                SmsSendingHistory.objects.create(user_id=user_id, phone=phone_to, sms_code=self.random_string)
                return {"status": "success", "message": "Sms was sent successfully!"}

            except TwilioException as exception:
                print (exception)
                return {"status": "error", "message": exception}
