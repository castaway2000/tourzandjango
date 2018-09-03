from django import forms
from .models import *
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from django.utils.translation import ugettext as _
from string import Template
from django.utils.safestring import mark_safe
import datetime
from dateutil.relativedelta import relativedelta


class GuideProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    city_search_input = forms.CharField(required=True)
    date_of_birth = forms.DateTimeField(input_formats=['%m/%d/%Y'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))

    class Meta:
        model = GuideProfile
        #city is added on form save in view
        fields = ("overview", "profile_image", "license_image", "rate", "is_active", "is_default_guide", "min_hours",)


class BookingGuideForm(forms.Form):
    # , widget=forms.HiddenInput()
    date = forms.DateTimeField(required=True, widget=forms.TimeInput(format='%m/%d/%Y %H:%M'), label=_("Offer date and time"))
    guide_id = forms.ChoiceField(required=True)
    hours = forms.IntegerField(required=True, min_value=1)
    number_people = forms.IntegerField(required=True, min_value=2)
    message = forms.CharField(required=False, widget=forms.Textarea({"rows": 3}), label=_("Your initial message to guide"))

    def __init__(self, *args, **kwargs):
        self.max_persons_nmb = 3
        guide = kwargs.pop("guide")
        self.guide = guide

        super(BookingGuideForm, self).__init__(*args, **kwargs)
        self.fields['guide_id'] = forms.ChoiceField(
            choices=[(guide.id, guide.id)]
        )
        self.fields['guide_id'].widget = forms.HiddenInput()
        self.fields['hours'] = forms.IntegerField(required=True, min_value=guide.min_hours, max_value=8,
                                                  label=_("Hours duration (min: %s)" % guide.min_hours))
        self.fields['number_people'] = forms.IntegerField(required=True, min_value=1, max_value=self.max_persons_nmb,
                                                          label=_("Number people (max: %s)" % self.max_persons_nmb))
        self.helper = FormHelper(self)
        self.helper.form_tag = True

        layout = self.helper.layout = Layout()
        for field_name, field in self.fields.items():
            layout.append(Field(field_name, placeholder=field.label))
        self.helper.form_show_labels = False


        self.helper.layout.append(
            HTML(
                '<div class="mb10 text-center">'
                '<div><b>{}: </b>{}</div>'
                '<div><b>{}: </b>{}</div>'
                '<div><b>{}: </b>{} USD</div>'
                '<div class="text-center tour-price"><b>{}: </b><span class="price-value"><span id="price_total">{}</span> USD</span></div>'
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary btn-lg" type="submit">'
                '{}</button>'
                '</div>'
                '</div>'.format(_("Min hours"), self.guide.min_hours, _("Max persons"), self.max_persons_nmb, _("Rate per hour"), guide.rate,  _("Total price"), guide.rate, _('Submit'))
            ),
        )

    def clean_number_people(self):
        number_people = self.cleaned_data.get("number_people")
        if number_people > self.max_persons_nmb:
            raise forms.ValidationError(_("Maximum number of tour participants is: %s") % self.max_persons_nmb)
        return self.cleaned_data.get("number_people")
