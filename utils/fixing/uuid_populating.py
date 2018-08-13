import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from tours.models import Tour
from guides.models import GuideProfile, GuideAnswer
from orders.models import Order


"""
This script populates countries for the existing cities with no value in country field.
All the new cities will be populated with countries values automatically using a login in save method of City model
"""

def populate_uuids():
    # tours = Tour.objects.all()
    # for tour in tours.iterator():
    #     tour.save(force_update=True)


    guides = GuideProfile.objects.all()
    for guide in guides.iterator():
        try:
            guide.save(force_update=True)
        except:
            pass

    #
    # orders = Order.objects.all()
    # for order in orders.iterator():
    #     order.save(force_update=True)

    # guide_answers = GuideAnswer.objects.all()
    # for guide_answer in guide_answers.iterator():
    #     try:
    #         guide_answer.save(force_update=True)
    #     except:
    #         pass

if __name__ == "__main__":
    populate_uuids()