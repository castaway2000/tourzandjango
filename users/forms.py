from django import forms
from .models import *
from phonenumber_field.widgets import PhonePrefixSelect, PhoneNumberPrefixWidget
from allauth.account.models import EmailAddress


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        widgets = {'password': forms.PasswordInput()}


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
            raise forms.ValidationError("New phone should be different from current phone !")
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


class GeneralProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = GeneralProfile

        #city is added on form save in view
        fields = ("first_name", "last_name", "registration_country", "registration_state", "registration_city",
                  "registration_street",
                  "registration_building_nmb", "registration_flat_nmb", "registration_postcode", "is_company",
                  "business_id",
                  )

