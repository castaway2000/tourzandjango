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
    if not hasattr(user, 'guideprofile'):
        first_name = user.first_name
        if len(user.first_name) == 0:
            first_name = user.username
        else:
            name = first_name.strip().split(' ')[0]
            first_name = str(name[0]).upper() + str(name[1:]).lower()
        message = "This is your friendly customer representative Adam over at Tourzan.com. " \
                  "We were looking over our platform and found that you created a profile with us a while " \
                  "back. We wondered how many of our regular users also would be interested in being a local guide. " \
                  "Are you interested in showing others around your city for side cash? " \
                  "It is really easy to convert your current profile to a guide profile and get started, " \
                  "it takes less than 5 minues. Simply head over to tourzan.com, hit the become a guide button and " \
                  "login to get started. We hope to hear from you soon.".format(first_name)
        data = {"to_user": user, "to_email": user.email, 'subject': 'Consider becoming a Tourzan.com guide?', 'message': message}
        SendingEmail(data).sending_email(to_user=user, to_email=[user.email], subject='Consider becoming a Tourzan.com guide?',
                                         message=message)