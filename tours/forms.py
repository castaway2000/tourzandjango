from django import forms
from .models import *


class TourForm(forms.ModelForm):
    name = forms.CharField(required=True)
    class Meta:
        model = Tour
        fields = ("name", "overview", "payment_type", "is_active",)