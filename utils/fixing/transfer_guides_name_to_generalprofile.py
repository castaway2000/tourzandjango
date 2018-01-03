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
        profile.first_name = guide.name
        profile.save(force_update=True)

if __name__ == "__main__":
    transfer_name()