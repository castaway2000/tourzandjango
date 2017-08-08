from django import forms
from .models import *


class ContactUsMessageNotSignedInForm(forms.ModelForm):
    message = forms.CharField(required=True, widget=forms.Textarea)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = ContactUsMessage

        fields = ("message", "name", "email",)


class ContactUsMessageSignedInForm(forms.ModelForm):
    class Meta:
        model = ContactUsMessage

        fields = ("message",)