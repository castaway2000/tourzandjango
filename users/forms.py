from django import forms
from .models import *
from crequest.middleware import CrequestMiddleware
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())



class GeneralUserForm(forms.Form):
    current_password = forms.CharField(required = False, max_length=32, label="Password:",
                                 widget=forms.PasswordInput(attrs={'placeholder': 'Enter current password'}))
    password1 = forms.CharField(required = False, max_length=32, label="Password:",
                                 widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
    password2 = forms.CharField(required = False, max_length=32, label="Password Confirmation:",
                                 widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password again'}))



    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        cleaned_data = super(GeneralUserForm, self).clean()
        print cleaned_data



        print ("try")
        if cleaned_data['password1'] and cleaned_data['password2'] and cleaned_data['password1'] != cleaned_data['password2']:
            print ("not equal")
            print cleaned_data['password1']
            print cleaned_data['password2']

            raise forms.ValidationError("Passwords don't match. Please enter both fields again.")

        if (cleaned_data['password1'] and not cleaned_data['password2']) or (not cleaned_data['password1'] and cleaned_data['password2']):
            raise forms.ValidationError("Please fill in both fields for passwords.")

        return self.cleaned_data


    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not current_password:
            raise forms.ValidationError("Please enter current password.")
        else:
            return current_password


    def save(self, commit=True):
        print "save"

        request = CrequestMiddleware.get_request()
        user = request.user

        if self.cleaned_data['password1']:
            try:
                print ("user: %s" % user)
                # user = User.objects.get(username = self.cleaned_data['username'] )

                """
                saving password
                """
                if self.cleaned_data['password1']:
                    print(user)
                    print(self.cleaned_data['password1'])
                    user.set_password(self.cleaned_data['password1'])
                    user.save(update_fields=['password',])
                    update_session_auth_hash(request, user)

            except Exception as e:
                print (e)
                user = super(GeneralUserForm, self).save(commit=False)
                user.set_password(self.cleaned_data['password1'])
                if commit:
                    user.save()
                    update_session_auth_hash(request, user)