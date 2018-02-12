import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from users.models import GeneralProfile


def populate_uuids():
    general_profiles = GeneralProfile.objects.all()
    for general_profile in general_profiles.iterator():
        print(general_profile.id)
        general_profile.save(force_update=True)#uuid inserting is in save method if uuid field is empty

if __name__ == "__main__":
    populate_uuids()
