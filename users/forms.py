from django import forms
from .models import *
from phonenumber_field.widgets import PhonePrefixSelect, PhoneNumberPrefixWidget
from allauth.account.models import EmailAddress
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from allauth.account.forms import SignupForm
from tourzan.settings import GOOGLE_RECAPTCHA_SITE_KEY
from crequest.middleware import CrequestMiddleware
from django.urls import reverse


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        widgets = {'password': forms.PasswordInput()}
        fields = "referral_code"


class VerificationCodeForm(forms.Form):
    # phone = forms.RegexField(required=False, strip=True, regex='^\+([0-9]{,15})$')
    phone = forms.CharField()
    sms_code = forms.CharField(required=False)
    phone_formatted = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(VerificationCodeForm, self).__init__(*args, **kwargs)

    def clean_phone_formatted(self):
        user = self.user
        # phone = self.cleaned_data.get("phone")
        # print (self.cleaned_data.get("phone_formatted"))
        phone = self.cleaned_data.get("phone_formatted")
        if user.generalprofile.phone == phone:
            raise forms.ValidationError("New phone should be different from current phone!")
        if GeneralProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone belongs to other user!")
        return phone


    #logic for sms code verification
    def clean_sms_code(self):
        code_entering_limit = 3
        user = self.user
        sms_code = self.cleaned_data.get("sms_code")

        if not sms_code:
            pass
            # raise forms.ValidationError("This field is required.")
        else:
            sms = SmsSendingHistory.objects.filter(user=user).last()
            if sms:
                if sms.is_used == True:
                    raise forms.ValidationError("This sms code has been already used!")

                elif sms.tries_nmb >= code_entering_limit:
                    raise forms.ValidationError("You have reached the limit of tries nmb!")

                elif sms.sms_code == sms_code:
                    sms.is_used = True
                    sms.save(force_update=True)

                else:
                    sms.tries_nmb = sms.tries_nmb+1
                    sms.save(force_update=True)
                    raise forms.ValidationError("SMS code is incorrect!")
            else:
                raise forms.ValidationError("Please resend a code once again!")

        return sms_code


class GeneralProfileAsGuideForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateTimeField(input_formats=['%m.%d.%Y'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    sms_notifications = forms.BooleanField(required=False, label='Enable text notifications?')

    class Meta:
        model = GeneralProfile
        fields = ("first_name", "last_name", "date_of_birth", "registration_country", "registration_state", "registration_city",
                  "registration_street",
                  "registration_building_nmb", "registration_flat_nmb", "registration_postcode", "is_company",
                  "business_id", "sms_notifications",
                  )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user
        super(GeneralProfileAsGuideForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        user = self.user
        email = self.cleaned_data['email']
        if email != user.email:
            if User.objects.filter(email=email, is_active=True).exists():
                raise ValidationError(_('Email already in use by another user'))
        return email


class GeneralProfileAsTouristForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    sms_notifications = forms.BooleanField(required=False, label='Enable text notifications?')
    class Meta:
        model = GeneralProfile
        fields = ("first_name", "last_name", "sms_notifications",)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = self.request.user
        super(GeneralProfileAsTouristForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email
        self.helper = FormHelper()
        self.helper.form_tag = True

    def clean_email(self):
        user = self.user
        new_email = self.cleaned_data['email']
        if new_email != user.email:
            if User.objects.filter(email=new_email, is_active=True).exists():
                raise ValidationError(_('Email already in use by another user'))
        return new_email


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'First name'}))
    agree_to_PP = forms.BooleanField(label="%s <a href='%s' target='_blank'>%s</a>" % (
                                                                                  _("I agree to"),
                                                                                  "/privacy-policy",
                                                                                  _("Privacy Policy"))
                                     )
    agree_to_TOS = forms.BooleanField(
        label="%s <a href='%s' target='_blank'>%s</a>" % (_("I agree to"), "/tos", _("Terms and Conditions"))
                                     )
    agree_to_emails = forms.BooleanField(label="%s" % (
        _("I accept and give my consent to receive emails concerning website updates, coupon codes and special offers."))
                                         ,help_text='Due to GDPR compliance we can only let you opt-in as a requirement. '
                                                    'We promise to not send a lot of useless emails.'
                                         )

    referral_code = forms.CharField(required=False, label=_('Referral code (optional)'))
    field_order = ('email', 'first_name', 'username', 'password1', 'password2',
                   'referral_code', 'agree_to_PP', 'agree_to_TOS', 'agree_to_emails',)

    # class Meta:
    #     fields = ['first_name', 'email', 'username', 'password1', 'password2', 'agree_to_PP',
    #                    'agree_to_TOS', 'agree_to_emails']

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        current_request = CrequestMiddleware.get_request()
        if current_request.session.get("referral_code"):
            self.fields['referral_code'].initial = current_request.session["referral_code"]

        self.helper = FormHelper(self)
        self.helper.label_class = 'text-left'
        self.helper.form_action = reverse('account_signup')
        self.helper.form_method = "post"
        # Add magic stuff to redirect back.
        self.helper.layout.append(
            HTML(
                "{% if redirect_field_value %}"
                "<input type='hidden' name='{{ redirect_field_name }}'"
                " value='{{ redirect_field_value }}' />"
                "{% endif %}"
            )
        )

        # Adding of google recapcha
        self.helper.layout.append(
            HTML(
                '<div class="form-group">'
                    '<div class="g-recaptcha" data-sitekey="' + GOOGLE_RECAPTCHA_SITE_KEY + '"></div>'
                '</div>'
            )
        )

        # Add submit button like in original form.
        self.helper.layout.append(
            HTML(
                '<div class="form-group text-center">'
                '<button class="btn btn-primary" type="submit">'
                '%s &raquo;</button>'
                '</div>' % _('Sign Up for Tourzan')
            ),
        )


class ExpressSignupForm(forms.Form):
    first_name = forms.CharField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    email = forms.EmailField(required=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Email'}))

    agree_to_PP = forms.BooleanField(label="%s <a href='%s' target='_blank'>%s</a>" % (
        _("I agree to"),
        "/privacy-policy",
        _("Privacy Policy"))
                                     )
    agree_to_TOS = forms.BooleanField(
        label="%s <a href='%s' target='_blank'>%s</a>" % (_("I agree to"), "/tos", _("Terms and Conditions"))
    )
    agree_to_emails = forms.BooleanField(label="%s" % (
        _(
            "I accept and give my consent to receive emails concerning website updates, coupon codes and special offers."))
                                         ,
                                         help_text='Due to GDPR compliance we can only let you opt-in as a requirement. '
                                                   'We promise to not send a lot of useless emails.'
                                         )

    def __init__(self, *args, **kwargs):
        super(ExpressSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = 'text-left'
        self.helper.form_method = "post"
        self.helper.layout.append(
            self.helper.layout.append(
                HTML(
                    '<div class="form-group text-center">'
                    '<button class="btn btn-primary" type="submit">%s'
                    '</button>'
                    '</div>' % _('proceed')
                ),
            )
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email is already in use. Please log in!'))
        return email


class ExpressSignupCompletingForm(CustomSignupForm):
    pass

    def __init__(self, *args, **kwargs):
        super(ExpressSignupCompletingForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.helper.form_action = ""#current url

    def clean_email(self):
        email = self.cleaned_data["email"]
        #doublecking apart of view that this user has unhashable password
        user = User.objects.filter(email=email).last()
        if user:
            if user.has_usable_password():
                raise ValidationError(_('Email is already in use. Please log in!'))
        if not user:
            #not sure, what is the possible case for this
            raise ValidationError(_('User with such email does not exist!'))
        return email