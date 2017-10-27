from django import forms
from .models import *


class DocsUploadingForm(forms.Form):
    file = forms.FileField(required=False)