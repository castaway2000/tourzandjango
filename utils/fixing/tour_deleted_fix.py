import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from tours.models import Tour
from utils.images_resizing import optimize_size


def tour_deleted_but_still_active():
    tours = Tour.objects.all()
    for tour in tours.iterator():
        if tour.is_deleted is True and tour.is_active is True:
            tour.is_active = False
            tour.save(force_update=True)


if __name__ == "__main__":
    # populate_uuids()
    populate_missed_images_for_tours()