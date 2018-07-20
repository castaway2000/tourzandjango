from django import forms
from .models import *
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from django.utils.translation import ugettext as _
from string import Template
from django.utils.safestring import mark_safe
import datetime


class GuideOrderAdjustForm(forms.ModelForm):
    # number_persons = forms.IntegerField(required=True, min_value=1)
    hours = forms.IntegerField(required=True, min_value=0)
    date_booked_for = forms.DateTimeField(required=True, widget=forms.TimeInput(format='%m/%d/%Y %H:%M'),
                                          label=_("Modify requested tour date and time and save it for tourist's approval"))

    class Meta:
        model = Order
        fields = ["hours", "date_booked_for"]

    def __init__(self, *args, **kwargs):
        super(GuideOrderAdjustForm, self).__init__(*args, **kwargs)
        tour = kwargs["instance"].tour if kwargs.get("instance") else None
        if tour:#hide hours for tours and let them be shown only for hourly guide bookings
            self.fields.pop("hours")

        self.helper = FormHelper(self)
        self.helper.form_tag = True

        self.helper.layout.append(
            HTML(
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Approve order')
            ),
        )