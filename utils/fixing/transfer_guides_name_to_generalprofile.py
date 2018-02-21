import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from guides.models import GuideProfile
from users.models import GeneralProfile


def transfer_name():
    guides = GuideProfile.objects.all()
    for guide in guides.iterator():
        profile, created = GeneralProfile.objects.get_or_create(user=guide.user)
        if not profile.first_name:
            if profile.user.first_name:
                profile.first_name = profile.user.first_name
            elif guide.name:
                profile.first_name = guide.name
            else:
                profile.first_name = guide.user.username

        if not profile.last_name:
            if profile.user.last_name:
                profile.last_name = profile.user.last_name

        if not profile.date_of_birth:
            profile.date_of_birth = guide.date_of_birth
        profile.save(force_update=True)

if __name__ == "__main__":
    transfer_name()