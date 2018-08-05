import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from locations.models import City, Country


"""
This script populates countries for the existing cities with no value in country field.
All the new cities will be populated with countries values automatically using a login in save method of City model
"""

def populate_countries():
    cities = City.objects.filter(place_id__isnull=False)
    for city in cities.iterator():
        city.save(force_update=True)

    countrys = Country.objects.all()
    for c in countrys:
        slug = str(c.name).replace(' ', '-').lower()
        c.slug = slug
        c.save(force_update=True)
        print(c.slug)

if __name__ == "__main__":
    populate_countries()