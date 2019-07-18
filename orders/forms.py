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
    date_booked_for = forms.DateTimeField(required=True, widget=forms.TimeInput(format='%m/%d/%Y %H:%M'),
                                          label=_("Modify requested tour date and time (if needed) or approve the current one"))

    class Meta:
        model = Order
        fields = ["hours_nmb", "date_booked_for"]

    def __init__(self, *args, **kwargs):
        super(GuideOrderAdjustForm, self).__init__(*args, **kwargs)
        self.order = kwargs["instance"]
        tour = kwargs["instance"].tour if kwargs.get("instance") else None
        self.tour = tour
        if tour:#hide hours for tours and let them be shown only for hourly guide bookings
            self.fields.pop("hours_nmb")
        else:
            self.fields['hours_nmb'] = forms.IntegerField(required=True, min_value=self.order.guide.min_hours, max_value=24,
                                                      label=_("Hours duration (min: %s)" % self.order.guide.min_hours))

        self.helper = FormHelper(self)
        self.helper.form_tag = True

        self.helper.layout.append(
            HTML(
                '<div class="text-left">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button> '
                '</div><div>%s</div>' % ( _('Change booking parameters*'), _("* You can do it before guide approved booking."))
            ),

        )

    def clean_hours_nmb(self):
        hours_nmb = self.cleaned_data["hours_nmb"]
        hours_min = self.tour.min_hours if self.tour else self.order.guide.min_hours
        if hours_min:
            if hours_min > hours_min:
                raise forms.ValidationError(_("Minimum number of hours is: %s") % self.max_persons_nmb)
        return hours_nmb

    def clean_number_people(self):
        number_people = self.cleaned_data.get("number_people")
        if number_people > self.max_persons_nmb:
            raise forms.ValidationError(_("Maximum number of tour participants is: %s") % self.max_persons_nmb)
        return self.cleaned_data.get("number_people")
