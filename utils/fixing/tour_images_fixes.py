import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from tours.models import Tour
from utils.images_resizing import optimize_size


def populate_missed_images_for_tours():#populate images for tours
    tours = Tour.objects.all()
    for tour in tours.iterator():
        if tour.image_large == "tours/images/default_tour_image_large.jpg":
            tour.image_large = optimize_size(tour.image, "large")
        tour.save(force_update=True)


if __name__ == "__main__":
    # populate_uuids()
    populate_missed_images_for_tours()