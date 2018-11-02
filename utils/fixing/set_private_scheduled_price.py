import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()

from tours.models import Tour, ScheduledTour


def set_private_price_same_as_scheduled():
    fixed_tours = []
    sch_tour = ScheduledTour.objects.all()
    for s in sch_tour:
        if s.tour.price < 1 and s.tour.id not in fixed_tours:
            print("private tour: %s, old price: %s, new price: %s" % (s.tour.id, s.tour.price, s.price))
            tour = Tour.objects.get(id=s.tour.id)
            tour.price = s.price
            tour.save(force_update=True)
            fixed_tours.append(tour.id)
set_private_price_same_as_scheduled()