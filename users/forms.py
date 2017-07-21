from django import forms
from .models import *


class DocsUploadingForm(forms.Form):
    file = forms.FileField(required=False)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
