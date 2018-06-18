from django import forms
from .models import *


class TourForm(forms.ModelForm):
    name = forms.CharField(required=True)
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Tour
        fields = ("name", "overview", "included", "excluded", "payment_type", "is_active",)

    def clean_name(self):
        if not self.cleaned_data.get("name"):
            raise forms.ValidationError("This field is required.")
        else:
            name = self.cleaned_data.get("name")
            tour_exist = Tour.objects.filter(name=name).exclude(id=self.instance.pk).exists()
            if tour_exist:
                raise forms.ValidationError("This tour name is already in use")

        return self.cleaned_data.get('name')