from django import forms
from .models import *
import pycountry


CHOICES = ( (country.name, country.name) for country in pycountry.countries )


class DocsUploadingForm(forms.Form):
    file = forms.FileField(required=True)

    registration_country = forms.ChoiceField(required=True, choices=CHOICES)
    registration_state = forms.CharField(required=False)
    registration_city = forms.CharField(required=True)
    registration_street = forms.CharField(required=True)
    registration_building_nmb = forms.CharField(required=True)
    registration_flat_nmb = forms.CharField(required=False)
    registration_postcode = forms.CharField(required=False)
