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


def login_view(request):
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
                return HttpResponseRedirect(reverse("home"))
            else:
                return HttpResponse("Your is disabled.")
        else:
            messages.error(request, 'Login credentials are incorrect!')

    return render(request, 'users/login_register.html', {})


def logout_view(request):
    user = request.user
    if not user.is_anonymous():
        logout(request)
    return HttpResponseRedirect(reverse("home"))


def home(request):
    current_page = "home"
    guides = GuideProfile.objects.filter(is_active=True)\
        .values("user__first_name", "user__last_name", "user__username", "profile_image", "overview")[:4]

    tours = Tour.objects.filter(is_active=True).order_by("-rating")
    all_tours = tours.order_by("-rating")[:4]
    hourly_tours = tours.filter(payment_type_id=1).order_by("-rating")[:4]
    fixed_payment_tours = tours.filter(payment_type_id=2).order_by("-rating")[:4]
    free_tours = tours.filter(is_free=True).order_by("-rating")[:4]
    cities = City.objects.filter(is_active=True, is_featured=True)[:5]
    return render(request, 'users/home.html', locals())


@login_required()
def general_settings(request):
    page = "general_settings"
    user = request.user
    general_profile, created = GeneralProfile.objects.get_or_create(user=user)

    form = PasswordChangeForm(data=request.POST or None, user=user)
    if request.method == 'POST':

        if form.is_valid():
            new_form = form.save(commit=False)
            new_form = form.save()
            messages.success(request, 'Password was successfully updated!')
            update_session_auth_hash(request, user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'users/general_settings.html', locals())



#this view is a based on the code of django view (django.views.i18n.py set_language() ), because there were [roblems with utf-8
#instruction how to use standard django approach for language changing using that view is described here:
#http://joaoventura.net/blog/2016/django-translation-4/
def set_language(request, language):
    print ("changing language")
    user_language = language
    next = request.META.get('HTTP_REFERER')
    next_trans = translate_url(next, user_language)
    response = HttpResponseRedirect(next_trans)

    if hasattr(request, 'session'):
        print ("has session")
    print (request.LANGUAGE_CODE)

    translation.activate(user_language)
    request.LANGUAGE_CODE = user_language
    print (request.LANGUAGE_CODE)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    request.session['django_language'] = user_language
    request.session[LANGUAGE_SESSION_KEY] = user_language
    print (request.session[LANGUAGE_SESSION_KEY])
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
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            response = self.form_valid(form)
        else:
            response = self.form_invalid(form)

        return _ajax_response(self.request, response, form=form)