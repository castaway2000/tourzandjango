import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import django
django.setup()
# from locations.models import City, Country
# import piexif
#
#
# def add_exif_location(image_file, country, city=None):
#     print("ADD EXIF")
#     print(piexif.load(image_file))