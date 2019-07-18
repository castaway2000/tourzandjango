from django import forms
from mobile.models import Waitlist


class WaitlistForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Please enter your name.')
    email = forms.EmailField(required=True, label='Please enter you Email.')
    city = forms.CharField(required=True, label='Please enter the city you live in.')
    country = forms.CharField(required=True, label='Please enter the country you live in.')
    comments = forms.Textarea()

    class Meta:
        model = Waitlist
