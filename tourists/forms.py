from django import forms
from .models import *


class TouristProfileForm(forms.ModelForm):

    class Meta:
        model = TouristProfile
        fields = ("image", "about",)