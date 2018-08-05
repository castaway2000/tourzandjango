import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
from locations.models import City, Country
from unsplash.api import Api
from unsplash.auth import Auth
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib.parse as urlparse
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


"""
This script populates countries for the existing cities with no value in country field.
All the new cities will be populated with countries values automatically using a login in save method of City model
"""

def get_image(search_term, image_name, unsplash_key=None):
    unsplash_keys = ["193597620d38bad554cbc25abc83facdb2edaf5f30c6b3c0e9309a2f65282237",
                     "b02b08dff59f76396a8baae8d6e981e41683954c2d68dabaab79b3233f2dcc39",
                     "b09fe903c14abd6b81434fcf821907617354c7a35bf463d9007c1420c15891b5",
                     "293d80bffd44a05e7f53e64685c039285c72feb87185397a58ccd927076bf0fe",
                     "0193a0e1b3b1ef396ab6ff1dc9f2845ef29d91fc194f4dca69605d3d0947e49a",
                     "71f7daecc23f75f0cf8fff3488a2cafe0040437d3240d8214e00379e6c337c0e",
                     "b036ac885ede0b5e6c803b97c770de3872b9fde6848adf4a359639d6a7612e95"]
    values = dict()
    values["client_id"] = unsplash_keys[0] if not unsplash_key else unsplash_key
    values["page"] = 1
    values["orientation"] = "landscape"
    url = "https://api.unsplash.com/photos/search/"
    values["query"] = search_term
    r = requests.get(url, values)
    import time
    if r.status_code == requests.codes.ok:
        images_data = r.json()
        results = dict()
        for photo in images_data:
            likes = photo["likes"]
            if len(results) == 0 or likes > results["likes"]:
                image_url = photo["urls"]["full"]
                parsed = urlparse.urlparse(image_url)
                get_parameters = urlparse.parse_qs(parsed.query)
                r = requests.get(image_url)
                if r.status_code == requests.codes.ok:
                    if get_parameters.get("fm"):
                        extension = get_parameters.get("fm")[0]
                        img_filename = "%s.%s" % (image_name, extension)
                        # country_wo_image.image.save(img_filename, File(img_temp), save = True)

                        # io = BytesIO(r.content)
                        results["likes"] = likes
                        results["data"] = (r.content, img_filename)

        if len(results) > 0:
            return results["data"]
        else:
            return (None, None)
    else:
        try:
            current_index = unsplash_keys.index("bar")
            next_index = current_index+1
            unsplash_key = unsplash_keys[next_index]
            get_image(search_term, image_name, unsplash_key)
        except:
            return (None, None)



def populate_countries():
    cities = City.objects.filter(place_id__isnull=False)
    for city in cities.iterator():
        city.save(force_update=True)

    countries = Country.objects.all()
    for country in countries.iterator():
        country.save(force_update=True)



    countries_wo_image = Country.objects.filter(image__isnull=True)
    if countries_wo_image:
        for country_wo_image in countries_wo_image.iterator():
            content, file_name = get_image(search_term=country_wo_image.name, image_name=country_wo_image.slug)
            if file_name:
                # country_wo_image.image.save(file_name, File(io), save=True)
                country_wo_image.image = SimpleUploadedFile(file_name, content)
                country_wo_image.save(force_update=True)


    cities_wo_image = City.objects.filter(image__isnull=True)
    if cities_wo_image:
        for city_wo_image in cities_wo_image.iterator():
            content, file_name = get_image(search_term=city_wo_image.name, image_name=city_wo_image.slug)
            if file_name:
                city_wo_image.image = SimpleUploadedFile(file_name, content)
                city_wo_image.save(force_update=True)


if __name__ == "__main__":
    populate_countries()