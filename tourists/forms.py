from django import forms
from .models import *
import os
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from utils.mixins import ImageCroppingMixin


class TouristProfileForm(ImageCroppingMixin, forms.ModelForm):
    image_field_name = "image"

    class Meta:
        model = TouristProfile
        fields = ("image", "about",)


class TouristTravelPhotoForm(forms.ModelForm):
    ALLOWED_TYPES = ['jpg', 'jpeg', 'png']
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = TouristTravelPhoto
        fields = ("image",)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TouristTravelPhotoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'mb10'
        self.helper.form_tag = True

        self.helper.layout.append(
            HTML('<div>'
                '<button class="btn btn-primary" type="submit">'
                '%s &raquo;</button>'
                '</div>' % _('Upload')
            ),
        )

    def clean_avatar(self):
        image = self.cleaned_data.get('image', None)
        if not image:
            raise forms.ValidationError('Missing image file')
        try:
            extension = os.path.splitext(image.name)[1][1:].lower()
            if extension in self.ALLOWED_TYPES:
                return image
            else:
                raise forms.ValidationError('File types is not allowed')
        except Exception as e:
            raise forms.ValidationError('Can not identify file type')