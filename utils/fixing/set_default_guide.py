import os
import sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../../")))
django.setup()
from guides.models import GuideProfile

gp = GuideProfile.objects.filter(is_default_guide=False)
for guide in gp:
    guide.is_default_guide = True
    guide.save()