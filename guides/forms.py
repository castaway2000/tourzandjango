from django import forms
from .models import *


class GuideProfileForm(forms.ModelForm):
    date_of_birth = forms.DateTimeField(input_formats=['%m.%d.%Y'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    class Meta:
        model = GuideProfile

        #city is added on form save in view
        fields = ("name", "overview", "date_of_birth", "profile_image")
