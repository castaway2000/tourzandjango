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
from utils.general import remove_zeros_from_float
import string


class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        html = Template("""<img src="$link" class="w100" />""")
        return mark_safe(html.substitute(link=value.url))


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


class TourGeneralForm(forms.ModelForm):
    name = forms.CharField()
    overview_short = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    overview = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    image = forms.ImageField(label=_('Tour main image'),required=False, \
                                    error_messages ={'invalid':_("Image files only")},\
                                    widget=forms.FileInput)
    hours = forms.DecimalField(required=True, min_value=1)
    included = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label=_("What is included?"))
    excluded = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label=_("What is excluded?"))
    type = forms.ChoiceField(choices=Tour().TOUR_TYPES, widget=forms.RadioSelect)

    class Meta:
        model = Tour
        fields = ("name", "overview_short", "overview", "hours", "included", "excluded", "image", "is_active", "type")

    def __init__(self, *args, **kwargs):
        super(TourGeneralForm, self).__init__(*args, **kwargs)
        self.image_small_url = None
        if hasattr(self, 'instance'):
            if self.instance.image_small:
                self.image_small_url = self.instance.image_small.url

        self.helper = FormHelper()
        self.helper.form_tag = True

        self.helper.layout = Layout(
            Field('is_active'),
            Field('type'),
            Field('name'),
            Field('overview_short'),
            Field('overview'),
            Field('hours'),
            Field('included'),
            Field('excluded'),
            Field('image'),
        )
        if self.image_small_url:
            self.helper.layout.append(
                HTML("<img class='w300 mb10' src='%s'/>" % self.image_small_url),
            )

        self.helper.layout.append(
                HTML('<div class="btn-toolbar text-center">'
                    '<a href="%s" class="btn btn-default">%s</a>'
                    '<button class="btn btn-primary" type="submit">'
                    '%s</button>'
                    '</div>' % (reverse("guide_settings_tours"), _("Cancel"),  _('Save'))
                ),
        )

    def clean_name(self):
        name = self.cleaned_data.get("name")

        #cheking if name text is in English
        try:
            name.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            raise forms.ValidationError(_('This field should contain only latin symbols'))

        if not name:
            raise forms.ValidationError(_('This field is required'))
        else:
            tour_exist = Tour.objects.filter(name=name).exclude(id=self.instance.pk).exists()
            if tour_exist:
                raise forms.ValidationError(_('This tour name is already in use'))

        return name


class TourProgramItemForm(forms.Form):
    name = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    day = forms.IntegerField(required=True)
    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    image = forms.ImageField(label=_('Upload new image below'),required=False, \
                                    error_messages ={'invalid':_("Image files only")},\
                                    widget=forms.FileInput)

    def __init__(self, *args, **kwargs):
        super(TourProgramItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True

        self.helper.layout = Layout(
            HTML('<input class="hidden" id="program_item_id" name="program_item_id">'),
            HTML('<img id="image" class="w300 img-responsive">'),
            Field('image'),
            Field('name'),
            Field('description'),
            Field('day'),
            Field('time'),

            HTML('<div class="btn-toolbar text-center">'
                '<a href="%s" class="btn btn-default" data-dismiss="modal" aria-label="Close">%s</a>'
                '<button class="btn btn-success" type="submit">'
                '%s</button>'
                '</div>' % (reverse("guide_settings_tours"), _("Cancel"),  _('Save'))
            ),
        )


class TourWeeklyScheduleTemplateForm(forms.ModelForm):
    time_start = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), label=_("Typical start time"))
    price = forms.DecimalField(required=True, min_value=0)
    seats_total = forms.IntegerField(required=True, min_value=0)

    class Meta:
        model = ScheduleTemplateItem
        fields = ("time_start", "price", "seats_total")



class TourWeeklyScheduleForm(forms.ModelForm):
    dt = forms.DateTimeField(widget=forms.TimeInput(format='%m/%d/%Y'), label=_("Date and time start"))
    time_start = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), label=_("Typical start time"))
    price = forms.DecimalField(required=True, min_value=0)
    discount = forms.DecimalField(required=True, min_value=0)
    seats_total = forms.IntegerField(required=True, min_value=0)

    class Meta:
        model = ScheduledTour
        fields = ("dt", "time_start", "price", "discount", "seats_total")

    def __init__(self, *args, **kwargs):
        super(TourWeeklyScheduleForm, self).__init__(*args, **kwargs)
        self.form_title = _("Create new Scheduled Item") if not kwargs.get("instance") else _("Edit Scheduled Item")
        self.price_final = kwargs["instance"].price_final if kwargs.get("instance") else 0
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout = Layout(
            HTML(
                '<div class="mt20"><h4>%s</h4></div>' % self.form_title
            ),

            Div(
                Field("dt"),
                Field("time_start"),

            ),
            Field("price"),
            Field("discount"),
            HTML("<div class='mb20'><b>%s </b> <span id='price_final'>%s</span></div>" % (_("Price final:"), self.price_final)),

            Field("seats_total"),
            HTML(
                '<div class="form-group text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Save')
            )
        )


class WeeklyTemplateApplyForm(forms.ModelForm):
    date_from = forms.DateField(required=True, label=_("Date from"))
    date_to = forms.DateField(required=True, label=_("Date to"))

    class Meta:
        model = ScheduleTemplateItem
        fields = ("date_from", "date_to")

    def __init__(self, *args, **kwargs):
        super(WeeklyTemplateApplyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout.append(
            HTML(
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Apply')
            ),
        )

    def clean_date_to(self):
        #prevent populating tours for period more than 3 months
        date_to = self.cleaned_data.get('date_to')
        today = datetime.datetime.today()
        month_limit = 3
        if date_to > (today + relativedelta(months =+ month_limit)).date():
            raise forms.ValidationError(_("Maximum period to choose is %s month." % month_limit))
        return self.cleaned_data.get('date_to')


class BookingScheduledTourForm(forms.Form):
    tour_scheduled = forms.ChoiceField(required=True, label=_("Selected tour date"))
    number_people = forms.IntegerField(required=True, initial=1, min_value=1)

    def __init__(self, *args, **kwargs):
        tour = kwargs.pop("tour")
        self.tour = tour
        super(BookingScheduledTourForm, self).__init__(*args, **kwargs)
        # self.fields['seats'].widget.attrs['min'] = 0
        self.fields['tour_scheduled'] = forms.ChoiceField(required=True, label=_("Select tour date"),
            choices=[(scheduled_tour.id, scheduled_tour.get_name()) for scheduled_tour in tour.get_nearest_available_dates(14)]
        )

        self.helper = FormHelper(self)
        self.helper.form_tag = True

        self.helper.layout.append(
            HTML(
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % _('Submit')
            ),
        )

    def clean_number_people(self):
        number_people = self.cleaned_data.get("number_people")
        tour_scheduled_id = self.cleaned_data.get("tour_scheduled")
        tour_scheduled = ScheduledTour.objects.get(id=tour_scheduled_id)

        if number_people > tour_scheduled.seats_available:
            raise forms.ValidationError(_("Maximum number of tour participants is: %s") % tour_scheduled.seats_available)
        return self.cleaned_data.get("number_people")


class BookingPrivateTourForm(forms.Form):
    # , widget=forms.HiddenInput()
    date = forms.DateTimeField(required=True, widget=forms.TimeInput(format='%m/%d/%Y %H:%M'))
    tour_id = forms.ChoiceField(required=True)
    number_people = forms.IntegerField(required=True, initial=1, min_value=1)
    message = forms.CharField(required=False, widget=forms.Textarea({"rows": 3}))

    def __init__(self, *args, **kwargs):
        tour = kwargs.pop("tour")
        self.tour = tour

        super(BookingPrivateTourForm, self).__init__(*args, **kwargs)
        self.fields['tour_id'] = forms.ChoiceField(
            choices=[(tour.id, tour.id)]
        )
        self.fields['tour_id'].widget = forms.HiddenInput()
        self.fields['number_people'] = forms.IntegerField(required=True, initial=1, min_value=1, max_value=self.tour.max_persons_nmb,
                                                          label=_("Number people (max: %s)" % tour.max_persons_nmb))

        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout.append(
            HTML(
                '<div class="tour-details-text">'
                '<div class="">1-{} {}: {} USD {}</div>'
                '<div class="">{}: {} USD {}</div>'
                '<div class="">{}: {}</div>'
                '</div>'
                '<div class="mb10">{}: <span id="price_total">{}</span> USD</div>'
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '{}</button>'
                '</div>'.format(tour.persons_nmb_for_min_price, _("persons"), remove_zeros_from_float(tour.price_final), _("for all"),
                                _("Additional people"), remove_zeros_from_float(tour.additional_person_price), _("for each person"),
                                _("Maximum participants"), tour.max_persons_nmb,
                                _("Total price") if not tour.discount else _("Total price with discount"),
                            tour.price_final, _('Submit'))
            ),
        )


    def clean_number_people(self):
        number_people = self.cleaned_data.get("number_people")
        if number_people > self.tour.max_persons_nmb:
            raise forms.ValidationError(_("Maximum number of tour participants is: %s") % self.tour.max_persons_nmb)
        return self.cleaned_data.get("number_people")


class PrivateTourPriceForm(forms.ModelForm):
    price = forms.DecimalField(required=True, min_value=1)
    discount = forms.DecimalField(required=True, min_value=0)
    persons_nmb_for_min_price = forms.IntegerField(required=True, min_value=2)
    max_persons_nmb = forms.IntegerField(required=True, min_value=2)#1 person more than persons_nmb_for_min_price
    additional_person_price = forms.DecimalField(required=True, min_value=0)

    class Meta:
        model = Tour
        fields = ("price", "persons_nmb_for_min_price", "max_persons_nmb", "additional_person_price", "discount")

    def __init__(self, *args, **kwargs):
        super(PrivateTourPriceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = True
        self.helper.layout.append(
            HTML(
                '<div class="mb10"><b>%s: </b><span id="price_final"></span> USD</div>'
                '<div class="text-center">'
                '<button name="action" class="btn btn-primary" type="submit">'
                '%s</button>'
                '</div>' % (_("Price final"), _('Apply'))
            ),
        )

    def clean_persons_nmb_for_min_price(self):
        persons_nmb_for_min_price = self.cleaned_data.get("persons_nmb_for_min_price")
        if persons_nmb_for_min_price < 2:
            raise forms.ValidationError(_("Persons number for minimum price can not be less than 2"))
        return self.cleaned_data.get("persons_nmb_for_min_price")


    def clean_max_persons_nmb(self):
        persons_nmb_for_min_price = self.cleaned_data.get("persons_nmb_for_min_price")
        max_persons_nmb = self.cleaned_data.get("max_persons_nmb")
        if persons_nmb_for_min_price > max_persons_nmb:
            raise forms.ValidationError(_("Persons number for minimum price can not be higher than maximum number of people in the tour"))
        return self.cleaned_data.get("max_persons_nmb")


    def clean_discount(self):
        price = self.cleaned_data.get("price")
        discount = self.cleaned_data.get("discount")
        if price - discount < 0:
            raise forms.ValidationError(_("Final price of the tour must be more than 0"))
        return self.cleaned_data.get("discount")
