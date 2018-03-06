from django import forms
from .models import *


class GuideProfileForm(forms.ModelForm):
    city_search_input = forms.CharField(required=True)
    date_of_birth = forms.DateTimeField(input_formats=['%m.%d.%Y'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    class Meta:
        model = GuideProfile
        #city is added on form save in view
        fields = ("overview", "profile_image", "rate", "is_active", "is_default_guide", "min_hours")