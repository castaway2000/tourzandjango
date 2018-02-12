import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from locations.models import City
from utils.images_resizing import optimize_size


def optimizing_images():
    cities = City.objects.all()
    for city in cities.iterator():
        if city.image:
            city.image = optimize_size(city.image, "large")
            city.image_medium = optimize_size(city.image, "medium")
            city.save(force_update=True)

if __name__ == "__main__":
    optimizing_images()