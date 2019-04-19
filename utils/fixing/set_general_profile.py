import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()

from django.contrib.auth.models import User
from users.models import GeneralProfile


def set_general_profile():
    for user in User.objects.all():
        print(user.username)
        profile, created = GeneralProfile.objects.get_or_create(user=user)
        if not profile.first_name:
            if profile.user.first_name:
                profile.first_name = profile.user.first_name or None
            elif user.first_name:
                profile.first_name = user.first_name or None
            else:
                profile.first_name = user.username or None
        if not profile.last_name:
            if profile.user.last_name:
                profile.last_name = profile.user.last_name or None
        profile.save(force_update=True)

if __name__ == "__main__":
    set_general_profile()