from django import forms
from .models import *


class PartnerForm(forms.ModelForm):
    company_name = forms.CharField(required=True)
    billing_address = forms.CharField(required=True, widget=forms.Textarea)
    tax_id = forms.CharField(required=False)
    website = forms.CharField(required=True)
    reason_requesting = forms.CharField(required=True, widget=forms.Textarea)
    requesting_person = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    is_agreed = forms.BooleanField(required=True)

    class Meta:
        model = Partner

        fields = ("company_name", "billing_address", "tax_id", "website", "reason_requesting", "requesting_person", "email")