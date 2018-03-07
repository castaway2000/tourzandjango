from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from tours.models import Tour
from orders.models import Review
from locations.models import City
from django.contrib.auth.models import User
from django.utils.translation import activate, get_language
from django.utils import translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.core.urlresolvers import translate_url
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from orders.models import Order
from guides.models import GuideProfile
from django.http import JsonResponse
from utils.internalization_wrapper import languages_english
from allauth.account.views import SignupView, _ajax_response
from tourzan.settings import GOOGLE_RECAPTCHA_SECRET_KEY
import requests
from utils.sending_sms import SendingSMS
from datetime import datetime
import pycountry
from allauth.account.models import EmailAddress
from django.utils.translation import ugettext as _


def login_view(request):
    """
    this funtion re-applies /login funtion from django-allauth/
    Login redirects are handled here
    """
    form = LoginForm(request.POST or None)

    if not "next" in request.GET:
        request.GET.next = reverse("home")
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if request.GET:
                    next_url = request.GET.get("next")
                    if next_url:
                        return HttpResponseRedirect(next_url)
                if user.guideprofile.is_default_guide:
                    request.session["current_role"] = "guide"
                if request.session.get("pending_order_creation"):
                    return HttpResponseRedirect(reverse("making_booking"))

                return HttpResponseRedirect(reverse("home"))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            messages.error(request, 'Login credentials are incorrect!')

    return render(request, 'users/login_register.html', {"form": form})


def logout_view(request):
    user = request.user
    if not user.is_anonymous():
        logout(request)
    return HttpResponseRedirect(reverse("home"))


@login_required()
def after_login_router(request):
    user = request.user
    print("after_login_router")
    print(HttpResponseRedirect(request.META.get('HTTP_REFERER')))
    pending_guide_registration = request.session.get("guide_registration_welcome_page_seen")
    if pending_guide_registration:
        return HttpResponseRedirect(reverse("guide_registration"))
    else:
        if user.generalprofile.is_previously_logged_in:
            return HttpResponseRedirect(reverse("home"))
        else:
            user.generalprofile.is_previously_logged_in = True
            user.generalprofile.save(force_update=True)
            return HttpResponseRedirect(reverse("profile_settings_tourist"))


def home(request):
    current_page = "home"
    guides = GuideProfile.objects.filter(is_active=True)\
        .values("user__generalprofile__first_name", "profile_image", "overview")[:4]

    tours = Tour.objects.filter(is_active=True).order_by("-rating")
    all_tours = tours.order_by("-rating")[:4]
    hourly_tours = tours.filter(payment_type_id=1).order_by("-rating")[:4]
    fixed_payment_tours = tours.filter(payment_type_id=2).order_by("-rating")[:4]
    free_tours = tours.filter(is_free=True).order_by("-rating")[:4]
    cities = City.objects.filter(is_active=True, is_featured=True).values("original_name", "image", "image_medium", "name")[:5]
    return render(request, 'users/home.html', locals())


@login_required()
def password_changing(request):
    user = request.user
    form = PasswordChangeForm(data=request.POST or None, user=user)
    if request.method == 'POST':
        if "change_password_btn" in request.POST:
            if form.is_valid():
                new_form = form.save(commit=False)
                new_form = form.save()
                messages.success(request, 'Password was successfully updated!')
                update_session_auth_hash(request, user)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'users/password_changing.html', locals())


@login_required()
def general_settings(request):
    page = "general_settings"
    user = request.user

    countries = [country.name for country in pycountry.countries]

    general_profile, created = GeneralProfile.objects.get_or_create(user=user)

    current_role = request.session.get("current_role")
    if current_role == "guide":
        guide = user.guideprofile
        form = GeneralProfileAsGuideForm(data=request.POST or None, instance=general_profile, request=request)
    else:
        form = GeneralProfileAsTouristForm(data=request.POST or None, instance=general_profile, request=request)

    verification_form = VerificationCodeForm(user, request.POST or None) #pass extra parameter here "user"

    if request.method == 'POST':
        # print(request.POST)

        #GeneralProfile form section
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form = form.save()

            user_email = user.email
            email = form.cleaned_data.get("email")
            if user_email.lower() != email.lower():
                #this validation is here and not in forms for not showing error message on form and for preventing signup users emails leak
                email_address_exists = EmailAddress.objects.filter(email=email).exclude(user=user).exists()

                #additional check to cope with lowercase emails, etc
                email_in_user_exists = User.objects.filter(is_active=True, email=email).exclude(id=user.id).exists()
                if email_address_exists or email_in_user_exists:
                    # print("ERROR")
                    pass
                else:
                    user.email = email
                    user.save()

                    #there is no email field on GeneralProfile model, so the logic for changing email is in this view only.
                    #this code is for triggering sending confirmation email function from django allauth
                    email_address = EmailAddress.objects.create(
                        user=request.user,
                        email=email,
                    )
                    email_address.send_confirmation(request)

                #this message is here to prevent signup users emails leaking
                messages.success(request, _('Your email address has been changed, please check you mailbox to confirm a new email address!'))

        #phone validation section
        data = request.POST
        # print("data %s" % data)

        if "phone_verification_cancel_btn" in data:

            #deleting session info if validation process is canceled
            if "pending_validating_phone" in request.session:
                del request.session["pending_validating_phone"]

            if "pending_sms_code" in request.session:
                del request.session["pending_sms_code"]


        elif "edit_phone" in data:
            phone = general_profile.phone

            #to show input field with current phone number
            request.session["pending_validating_phone"] = phone
            verification_form = VerificationCodeForm(user) #pass extra parameter here "user"

        elif "submit_phone_btn" in data:
            #to hide cancel button if the process has been started with sending code in sms
            request.session["pending_sms_code"] = True


        if verification_form.is_valid():

            # print("verification form is valid")

            if "submit_phone_btn" in data:
                # phone = data.get("phone")

                #phone_formatted field is a hidden input field where js intl-tel-input plugin puts data
                phone = data.get("phone_formatted")

                sms = SendingSMS({"phone_to": phone, "user_id": user.id})
                sms_sending_info = sms.send_validation_sms()
                if sms_sending_info["status"] == "success":
                    general_profile = user.generalprofile
                    general_profile.phone_pending = phone
                    general_profile.phone_is_validated = False
                    general_profile.save(force_update=True)
                    messages.success(request, 'SMS with validation code was sent!')
                    request.session["pending_validating_phone"] = phone
                else:#error
                    # message_text = sms_sending_info["message"]
                    message_text = _("Phone format is incorrect")
                    messages.error(request, message_text)

            #this approach is needed to prevent
            elif "validate_phone_btn" in data:
                if data.get("sms_code"):
                    general_profile.phone = general_profile.phone_pending
                    general_profile.phone_pending = ""
                    general_profile.phone_is_validated = True
                    general_profile.save(force_update=True)

                    #deleting session info if validation process is successfully completed
                    if "pending_validating_phone" in request.session:
                        del request.session["pending_validating_phone"]

                    if "pending_sms_code" in request.session:
                        del request.session["pending_sms_code"]
                    messages.success(request, 'Phone was successfully validated!')
                else:
                    messages.error(request, 'Please enter validation code!')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'users/general_settings.html', locals())



#this view is a based on the code of django view (django.views.i18n.py set_language() ), because there were [roblems with utf-8
#instruction how to use standard django approach for language changing using that view is described here:
#http://joaoventura.net/blog/2016/django-translation-4/
def set_language(request, language):
    # print ("changing language")
    user_language = language
    next = request.META.get('HTTP_REFERER')
    next_trans = translate_url(next, user_language)
    response = HttpResponseRedirect(next_trans)

    if hasattr(request, 'session'):
        # print ("has session")
        pass
    # print (request.LANGUAGE_CODE)

    translation.activate(user_language)
    request.LANGUAGE_CODE = user_language
    # print (request.LANGUAGE_CODE)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    request.session['django_language'] = user_language
    request.session[LANGUAGE_SESSION_KEY] = user_language
    # print (request.session[LANGUAGE_SESSION_KEY])
    return response


@login_required()
def change_role(request, new_role=None):
    user = request.user
    if not user.is_anonymous() and hasattr(user, 'guideprofile'):
        current_role = request.session.get("current_role")
        if current_role == "tourist" or not current_role:
            request.session["current_role"] = "guide"
            messages.success(request, 'Switched to guide profile!')
        else:
            request.session["current_role"] = "tourist"
            messages.success(request, 'Switched to tourist profile!')
    else:
        request.session["current_role"] = "tourist"
        return HttpResponseRedirect(reverse("guide_registration_welcome"))

    #new_role option is goes from settings page switching to another user
    if new_role:
        return HttpResponseRedirect(reverse("settings_router"))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def settings_router(request):
    current_role = request.session.get("current_role")
    if current_role == "guide":
        return HttpResponseRedirect(reverse("profile_settings_guide"))
    elif current_role == "tourist" or not current_role:
        request.session["current_role"] = "tourist"
        return HttpResponseRedirect(reverse("profile_settings_tourist"))


def search_interest(request):
    print ("search_interest")
    response_data = dict()
    results = list()

    if request.GET:
        data = request.GET
        print (data)
        interest_name = data.get(u"q")
        interests = Interest.objects.filter(name__icontains=interest_name)

        for interest in interests:
            results.append({
                "id": interest.name,
                "text": interest.name
            })

    response_data = {
        "items": results,
        "more": "false"
    }

    print (response_data)
    return JsonResponse(response_data, safe=False)


def search_language(request):
    response_data = dict()
    results = list()

    if request.GET:
        data = request.GET
        language_name = data.get(u"q").lower()
        languages = [item for item in languages_english]
        for language in languages:
            language_name_text = language[1].lower()
            if language_name in language_name_text:
                results.append({
                    "id": language[0],
                    "text": language[1]
                })

    response_data = {
        "items": results,
        "more": "false"
    }
    return JsonResponse(response_data, safe=False)


#redefining allauth SignUp view to cope with a bug when at login page user tries to signup and then to log in
class SignupViewCustom(SignupView):

    # at the initial SignupView this post function is inherited from AjaxCapableProcessFormViewMixin
    # so here a post function from AjaxCapableProcessFormViewMixin is redefined
    def post(self, request, *args, **kwargs):

        if u"login_btn" in request.POST:
            return HttpResponseRedirect(reverse("login"))

        #google captcha validating
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if recaptcha_response and recaptcha_response != "":
            data = {
                'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
                pass
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            response = self.form_valid(form)
        else:
            response = self.form_invalid(form)

        return _ajax_response(self.request, response, form=form)


@login_required()
def sending_sms_code(request):
    user = request.user
    print(request.POST)

    return_data = dict()
    if request.POST:
        print (request.POST)
        data = request.POST

        # phone = data.get("phone")

        #phone_formatted field is a hidden input field where js intl-tel-input plugin puts data
        phone = data.get("phone_formatted")

        sms = SendingSMS({"phone_to": phone, "user_id": user.id})
        sms_sending_status = sms.send_validation_sms()

        print("sms status %s" % sms_sending_status)
        return_data["status"] = sms_sending_status

        if sms_sending_status == "success":
            general_profile = user.generalprofile
            general_profile.phone = phone
            general_profile.phone_is_verified = False
            general_profile.save(force_update=True)

    return JsonResponse(return_data)
