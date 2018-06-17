from django import forms
from .models import *
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.urls import reverse


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


class BookingForm(forms.Form):
    tour_scheduled = forms.ChoiceField(required=True, label=_("Selected tour date"))
    number_people = forms.IntegerField(required=True, initial=1, min_value=1)

    def __init__(self, *args, **kwargs):
        tour = kwargs.pop("tour")
        super(BookingForm, self).__init__(*args, **kwargs)
        # self.fields['seats'].widget.attrs['min'] = 0
        self.fields['tour_scheduled'] = forms.ChoiceField(
            choices=[(scheduled_tour.id, scheduled_tour.get_name()) for scheduled_tour in tour.get_nearest_available_dates()]
        )

        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.form_action = reverse('making_booking')

        self.helper.layout.append(
            HTML(
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Submit')
            ),
        )