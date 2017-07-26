from django import forms
from .models import *



class DocsUploadingForm(forms.Form):
    file = forms.FileField(required=False)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        widgets = {'password': forms.PasswordInput()}


class VerificationCodeForm(forms.Form):
    phone = forms.RegexField(required=False, strip=True, regex='^\+([0-9]{,15})$')
    sms_code = forms.CharField(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(VerificationCodeForm, self).__init__(*args, **kwargs)


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

        return self.cleaned_data.get('sms_code')
