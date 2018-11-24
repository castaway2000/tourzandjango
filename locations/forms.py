from django import forms
from .models import NewLocationTourRequest
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.conf import settings


class NewLocationTourRequestForm(forms.ModelForm):
    tour_date = forms.DateTimeField(widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M'))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4}), max_length=3000)
    number_persons = forms.IntegerField(required=True, min_value=1, max_value=2, label=_("People nmb"))

    class Meta:
        model = NewLocationTourRequest
        fields = ("tour_date", "number_persons", "description", "email", "first_name")

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user") if "user" in kwargs else None
        super(NewLocationTourRequestForm, self).__init__(*args, **kwargs)
        self.fields['number_persons'].initial = 1
        if not user.is_anonymous():
            self.fields.pop("email")
            self.fields.pop("first_name")
        else:
            self.fields['email'] = forms.EmailField(required=True, label=_("Your email"))
            self.fields['first_name'] = forms.EmailField(required=True, label=_("Your first name"))
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout.append(
            HTML(
                '<div class="form-group">'
                '<div class="g-recaptcha" data-sitekey="' + settings.GOOGLE_RECAPTCHA_SITE_KEY + '"></div>'
                                                                                        '</div>'
            )
        )
        self.helper.layout.append(
            HTML(
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Submit')
            ),
        )