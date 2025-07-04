from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from .forms import *
from .models import *
from tours.models import Tour, ScheduledTour
from partners.models import IntegrationPartners, Endorsement
from website_management.models import InTheNews

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
from django.http import JsonResponse, HttpResponseForbidden
from utils.internalization_wrapper import languages_english
from allauth.account.views import SignupView, LoginView, _ajax_response
from tourzan.settings import GOOGLE_RECAPTCHA_SITE_KEY, GOOGLE_RECAPTCHA_SECRET_KEY
import requests
from utils.sending_sms import SendingSMS
import datetime
import pycountry
from allauth.account.models import EmailAddress
from django.utils.translation import ugettext as _
from coupons.models import Coupon, CouponUser, Campaign
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.exceptions import ImmediateHttpResponse
import time
from website_management.models import HomePageContent
from locations.models import Country
import urllib.parse as urlparse
from .forms import ExpressSignupForm
from utils.sending_emails import SendingEmail
from allauth.account.utils import get_next_redirect_url
from utils.locations import get_city_country


def logout_view(request):
    user = request.user
    if not user.is_anonymous():
        logout(request)
    return HttpResponseRedirect(reverse("home"))


@login_required()
def after_login_router(request):
    user = request.user
    pending_guide_registration = request.session.get("guide_registration_welcome_page_seen")
    if pending_guide_registration:
        return HttpResponseRedirect(reverse("guide_registration"))
    else:
        if user.generalprofile.is_previously_logged_in:
            if hasattr(user, "guideprofile") and user.guideprofile.is_default_guide:
                request.session["current_role"] = "guide"
            elif not hasattr(user, "guideprofile"):
                messages.success(request, "<h4><a href='https://www.tourzan.com%s'>%s</a></h4>" % (
                    reverse("guide_registration_welcome"),
                    _("We see you are not a guide yet, you should consider being a guide!")), 'safe')
            if request.session.get("pending_order_creation"):
                return HttpResponseRedirect(reverse("making_booking"))
            else:
                return HttpResponseRedirect(reverse("home"))
        else:
            user.generalprofile.is_previously_logged_in = True
            user.generalprofile.save(force_update=True)
            return HttpResponseRedirect(reverse("profile_settings_tourist"))


def home(request):
    current_page = "home"
    # guides = GuideProfile.objects.filter(is_active=True)\
    #     .values("user__generalprofile__first_name", "user__generalprofile__uuid", "user__username", "profile_image", "overview")[:4]
    #
    # tours = Tour.objects.filter(is_active=True).order_by("-rating")
    # all_tours = tours.order_by("-rating")[:4]
    # hourly_tours = tours.filter(payment_type_id=1).order_by("-rating")[:4]
    # fixed_payment_tours = tours.filter(payment_type_id=2).order_by("-rating")[:4]
    # free_tours = tours.filter(is_free=True).order_by("-rating")[:4]
    # cities = City.objects.filter(is_active=True, is_featured=True)\
    #              .values("original_name", "image", "image_medium", "name", "slug", "country__slug")[:10]

    src = request.GET.get("src")
    city = None
    if src:
        city_slug = src
        city, country = get_city_country(city_slug=city_slug)
    try:
        obj = HomePageContent.objects.last()
    except:
        obj = None
    countries = Country.objects.filter(is_active=True).order_by("position_index")
    cities_count = City.objects.all().count()
    print(countries.count())
    # special_offers_items = Tour.objects.filter(is_active=True)
    # special_offer_tours = list()
    # count = 0
    # for special_offers_item in special_offers_items.iterator():
    #     if len(special_offers_item.available_discount_tours()) > 0:
    #         special_offer_tours.append(special_offers_item)
    #         if count == 4:
    #             break
    #         count += 1
    partners = IntegrationPartners.objects.filter(is_active=True)[:8]
    featured_news = InTheNews.objects.filter(is_active=True)[:4]
    endorsements = Endorsement.objects.filter(is_active=True)[:8]
    #
    # now = datetime.datetime.now().date()
    # limit_days = now + datetime.timedelta(days=30)
    # discount_scheduled_tours = ScheduledTour.objects.filter(is_active=True, seats_available__gt=0, discount__gt=0)
    # special_offer_tours = list()
    # for discount_scheduled_tour in discount_scheduled_tours.iterator():
    #     tour = discount_scheduled_tour.tour
    #     if not tour in special_offer_tours:
    #         special_offer_tours.append(tour)


    context = {
        "obj": obj,
        "current_page": current_page,
        "countries": countries[:6],
        "countries_count": countries.count(),
        "cities_count": cities_count,
        # "special_offer_tours": special_offer_tours,
        "partners": partners,
        "featured_news": featured_news,
        "endorsements": endorsements,
    }
    if city:
        context["city"] = city
    return render(request, 'users/home.html', context)


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
        #GeneralProfile form section
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form = form.save()
            messages.success(request, 'profile saved')

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
                    email_address = EmailAddress.objects.update_or_create(  # TODO make this better
                        user=request.user,
                        email=email,
                    )
                    email_address[0].send_confirmation(request)

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

                sms = SendingSMS()
                sms_sending_info = sms.send_validation_sms(phone_to=phone, user_id=user.id)
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
                    general_profile.sms_notifications = True
                    general_profile.save(force_update=True)
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
    new_role = False
    if not user.is_anonymous() and hasattr(user, 'guideprofile'):
        current_role = request.session.get("current_role")
        if current_role == "tourist" or not current_role:
            request.session["current_role"] = "guide"
            messages.success(request, 'Switched to guide profile!')
        else:
            request.session["current_role"] = "tourist"
            messages.success(request, 'Switched to tourist profile!')
        return HttpResponseRedirect(reverse("settings_router"))
    else:
        request.session["current_role"] = "tourist"
        return HttpResponseRedirect(reverse("guide_registration_welcome"))


@login_required()
def settings_router(request):
    current_role = request.session.get("current_role")
    print(current_role)
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


class LoginViewCustom(LoginView):

    def get_success_url(self):
        self.success_url = reverse("after_login_router")
        ret = (get_next_redirect_url(
            self.request,
            self.redirect_field_name) or self.success_url)
        return ret

#redefining allauth SignUp view to cope with a bug when at login page user tries to signup and then to log in
class SignupViewCustom(SignupView):

    def get_success_url(self):
        request = self.request
        if request.session.get("pending_order_creation"):
            self.success_url = reverse("making_booking")

        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or self.success_url)
        return ret

    def get_context_data(self, **kwargs):
        context = super(SignupViewCustom, self).get_context_data(**kwargs)
        context["recaptcha_site_key"] = GOOGLE_RECAPTCHA_SITE_KEY
        return context

    def form_valid(self, form):
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance
        self.user = form.save(self.request)
        try:
            return complete_signup(
                self.request, self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response

    # at the initial SignupView this post function is inherited from AjaxCapableProcessFormViewMixin
    # so here a post function from AjaxCapableProcessFormViewMixin is redefined
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # google captcha validating
        google_captcha_is_valid = False
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if recaptcha_response and recaptcha_response != "":
            data = {
                'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
                google_captcha_is_valid = True
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                response = self.form_invalid(form)
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            response = self.form_invalid(form)

        if form.is_valid() and google_captcha_is_valid:
            response = self.form_valid(form)
            referral_code = None
            if "referral_code" in self.request.session:
                referral_code = self.request.session.get("referral_code")
            elif request.POST.get('referral_code'):
                referral_code = request.POST.get('referral_code')

            if referral_code and referral_code != "":
                #in this step not only tourists can be referred, but guides as well, so reffered by is set to generalprofile,
                #which is related to user by OneToOne field
                #Dublicate this logic for API singup functionality later
                #AT 04112018: it is implemented, because this flow is used in at least one more place (completing express signup)
                request.user.generalprofile.apply_referral_code(referral_code)

            #creating Tourist Profile (moved here from
            if u"login_btn" in request.POST:
                return HttpResponseRedirect(reverse("login"))

        else:
            response = self.form_invalid(form)
        return _ajax_response(self.request, response, form=form)


@login_required()
def sending_sms_code(request):
    user = request.user
    return_data = dict()
    if request.POST:
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


@login_required()
def promotions(request):
    return render(request, 'users/promotions.html', locals())


def authorization_options(request):
    user = request.user
    if not user.is_anonymous():
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse("home")))
    else:
        form = ExpressSignupForm(request.POST or None)
        if request.POST and form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            email = form.cleaned_data.get("email")
            user = User.objects.create(username=email, email=email)
            user.set_unusable_password()

            general_profile = user.generalprofile
            general_profile.first_name = first_name
            general_profile.is_express_signup_initial = True
            general_profile.is_express_signup_current = True
            general_profile.save(force_update=True)

            #sending email with link to continue checkout
            SendingEmail({"user": user}).email_for_express_signup()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.session.get("pending_order_creation"):
                return HttpResponseRedirect(reverse("making_booking"))
            else:
                return HttpResponseRedirect(reverse("home"))
        return render(request, 'users/authorization_options.html', locals())


def express_signup_completing(request, uuid):
    general_profile = get_object_or_404(GeneralProfile, uuid=uuid)
    user = general_profile.user
    if user.has_usable_password():
        return HttpResponseForbidden()
    else:
        form = ExpressSignupCompletingForm(request.POST or None, initial={"email": user.email, "first_name": user.first_name})
    if request.POST and form.is_valid():
        print(request.POST)
        password = form.cleaned_data["password1"]
        username = form.cleaned_data["username"]
        first_name = form.cleaned_data["first_name"]
        referral_code = form.cleaned_data["referral_code"]

        #updating info for user
        user.set_password(password)
        user.username = username
        user.save(force_update=True)

        #updating info for user profile
        general_profile = user.generalprofile
        general_profile.first_name = first_name
        general_profile.is_express_signup_current = False
        general_profile.save(force_update=True)
        general_profile.apply_referral_code(referral_code)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, _('Successfully signed up!'))
        return HttpResponseRedirect(reverse("home"))
    return render(request, 'users/express_signup_completing.html', locals())
