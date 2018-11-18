from django import forms
from io import BytesIO
from PIL import Image
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile


class ImageCroppingMixin(forms.Form):
    """
    Include this mixing to a form class at the first place: class SomeForm(ImageCroppingMixin, forms.Form)
    """
    image_field_name = "avatar" #  !!!This should be re-applied on the model if the field of the avatar has different name
    # fields for image cropping are below
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super(ImageCroppingMixin, self).clean()
        image_field_name = self.image_field_name
        avatar = self.cleaned_data[image_field_name]
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if avatar and w and h:
            with Image.open(avatar) as initial_image:
                exif = None
                try:
                    exif = initial_image._getexif()
                except:
                    pass

                # if image has exif data about orientation, let's rotate it

                # cf ExifTags
                orientation_key = 274
                if exif and orientation_key in exif:
                    orientation = exif[orientation_key]

                    rotate_values = {
                        3: Image.ROTATE_180,
                        6: Image.ROTATE_270,
                        8: Image.ROTATE_90
                    }

                    if orientation in rotate_values:
                        initial_image.transpose(rotate_values[orientation])

                image = initial_image.crop((x, y, w + x, h + y))
                image.thumbnail((250, 250), Image.ANTIALIAS)

                output = BytesIO()
                try:
                    image.save(output, format='JPEG', quality=100)
                    output.seek(0)
                    img = InMemoryUploadedFile(
                        output, 'ImageField', "%s" % avatar.name,
                        'image/jpeg', sys.getsizeof(output), None)
                except Exception as e:
                    image.convert('RGB').save(
                        output, format='JPEG', quality=100)
                    output.seek(0)
                    img = InMemoryUploadedFile(
                        output, 'ImageField', "%s" % avatar.name,
                        'image/jpeg', sys.getsizeof(output), None)
            cleaned_data[image_field_name] = img
        else:
            cleaned_data[image_field_name] = avatar
        return cleaned_data
