from django import forms
from .models import *


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class TouristProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ("image", "about",)


class GuideProfileForm(forms.ModelForm):
    date_of_birth = forms.DateTimeField(input_formats=['%m.%d.%Y'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    class Meta:
        model = GuideProfile

        #city is added on form save in view
        fields = ("name", "overview", "date_of_birth", "profile_image")
