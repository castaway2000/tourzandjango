from django import forms
from .models import *
from crequest.middleware import CrequestMiddleware
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
