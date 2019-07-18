import os
import sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../../")))
django.setup()
from django.contrib.auth.models import User
from utils.sending_emails import SendingEmail


user = User.objects.all()
for user in user.iterator():
    m1 = False
    m2 = False
    if len(str(user.touristprofile.image)) == 0:
        m1 = True
    if hasattr(user, 'guideprofile'):
        if len(str(user.guideprofile.profile_image)) == 0:
            m2 = True

    if m1 and m2:
        message = "Tourzan.com's has been doing routine maintenance to make sure we are providing the highest quality " \
                  "to you and our customers. During one of our tests We discovered that both your tourist and guide " \
                  "profile are lacking profile pictures. We would like to take this time to let you know that an " \
                  "engaging profile picture is a pillar of success on Tourzan.com and we encourage you to update " \
                  "your profile as soon as it is convenient to you."
    elif m1 and not m2:
        message = "Tourzan.com's has been doing routine maintenance to make sure we are providing the highest quality " \
                  "to you and our customers. During one of our tests We discovered that your tourist " \
                  "profile is lacking profile picture. We would like to take this time to let you know that an " \
                  "engaging profile picture is a key to connecting with locals on Tourzan.com and we encourage you " \
                  "to update your profile as soon as it is convenient to you."
    elif m2 and not m1:
        message = "Tourzan.com's has been doing routine maintenance to make sure we are providing the highest quality " \
                  "to you and our customers. During one of our tests We discovered that your guide " \
                  "profile is lacking a profile picture. We would like to take this time to let you know that an " \
                  "engaging profile picture is one of many pillars of success on Tourzan.com and we encourage you " \
                  "to update your profile as soon as it is convenient to you."

    data = {"to_user": user, "to_email": user.email, 'subject': 'Consider becoming a Tourzan.com guide?', 'message': message}
    SendingEmail(data).sending_email(to_user=user, to_email=[user.email], subject='Consider becoming a Tourzan.com guide?',
                                     message=message)