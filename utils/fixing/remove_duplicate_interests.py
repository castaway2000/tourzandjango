import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()

from users.models import Interest, UserInterest


def remove_duplicate_interests():
    interests = Interest.objects.all().filter()
    for i in interests:
        i.save(force_update=True)
        dupes = Interest.objects.filter(name=i.name)
        if len(dupes) > 1:
            user_interest = UserInterest.objects.filter(interest=i)
            for u in user_interest:
                print(dupes[0].id)
                u.interest = dupes[0]
                u.save(force_update=True)
            for d in dupes[1:]:
                print(d.id)
                Interest.objects.filter(id=d.id).delete()


remove_duplicate_interests()