import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from users.models import GeneralProfile


def reset_to_false():
    users = GeneralProfile.objects.all()
    for user in users.iterator():
        print(user.user.username)
        user.sms_notifications = False
        user.save(force_update=True)

def sms_opt_out_setup():
    users = GeneralProfile.objects.all()
    for user in users.iterator():
        if user.sms_notifications is False and user.phone_is_validated is True:
            print(user.user.username)
            user.sms_notifications = True
            user.save(force_update=True)

if __name__ == "__main__":
    print('RESETTING TO FALSE FOR SMS NOTIFICATIONS')
    reset_to_false()
    print('SETTING OPT-IN')
    sms_opt_out_setup()