from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from tours.models import Tour, Review
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
    hourly_tours = tours.filter(payment_type_id=1).order_by("-rating")[:4]
    fixed_payment_tours = tours.filter(payment_type_id=2).order_by("-rating")[:4]
    free_tours = tours.filter(is_free=True).order_by("-rating")[:4]
    cities = City.objects.filter(is_active=True, is_featured=True)[:5]
    return render(request, 'users/home.html', locals())


def guide(request, username):
    user = request.user
    if username:
        try:
            guide_user = User.objects.get(username=username)
        except:
            return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))

    if not guide_user.guideprofile:
        return HttpResponseRedirect(reverse("home"))

    guide = guide_user.guideprofile

    tours = guide.tour_set.filter(is_active=True)
    tours_ids = [tour.id for tour in tours]
    reviews = Review.objects.filter(is_active=True, id__in=tours_ids)

    guide_services = GuideService.objects.filter(guide=guide).values("service__name")

    if request.POST:
        data = request.POST
        print (data)
        if data.get("text") and user:
            kwargs = dict()
            kwargs["text"] = data.get("text")
            if data.get("name"):
                kwargs["name"] = data.get("name")

            kwargs["rating"] = 5

            review, created = Review.objects.update_or_create(user=user, defaults=kwargs)

            if created:
                #add messages here
                pass

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        "guide": guide,
        "tours": tours,
        "reviews": reviews,
        "guide_services": guide_services
    }
    return render(request, 'users/guide.html', context)


    """
    some example for spiltting interests. It need to be reviewed later
    """
    # form = ProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    #
    # if request.method == 'POST' and form.is_valid():
    #     new_form = form.save(commit=False)
    #     new_form = form.save()
    #
    #     #for future search functionality by interests: they are saved to separate table
    #     # to be displayed as a list in Search Page
    #     interests = form.cleaned_data.get("interests")
    #     if interests:
    #         interests_list = interests.split(", ")
    #         for interest_name in interests_list:
    #             Interest.objects.get_or_create(name=interest_name)
    #
    #     messages.success(request, 'New artist was successfully created!')
    #
    # # for pictures: http://ashleydw.github.io/lightbox/
    # context = {
    #     'user_profile': user_profile,
    #     'form': form
    # }
    # return render(request, 'users/profile_settings.html', locals())


@login_required()
def profile_settings_guide(request):
    page = "profile_settings_guide"
    user = request.user
    guide = user.guideprofile
    if guide:
        form = GuideProfileForm(request.POST or None, request.FILES or None, instance=guide)
    else:
        form = GuideProfileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        print (request.POST)

        interests = request.POST.getlist("interests")
        user_interest_list = list()
        if interests:
            for interest in interests:
                interest, created = Interest.objects.get_or_create(name=interest)

                #adding to bulk create list for faster creation all at once
                user_interest_list.append(UserInterest(interest=interest, user=user))


        UserInterest.objects.filter(user=user).delete()
        UserInterest.objects.bulk_create(user_interest_list)


        #saving services
        guide_services_list = list()
        for name, value in request.POST.items():
            string_key = "service_"
            if name.startswith(string_key):

                cleared_name = name.partition(string_key)[2]#getting part of the variable name which is field name
                service = Service.objects.get(html_field_name=cleared_name)
                guide_services_list.append(GuideService(service=service, guide=guide))

        GuideService.objects.filter(guide=guide).delete()
        GuideService.objects.bulk_create(guide_services_list)


        #To review this approach in the future
        city = request.POST.get("city")
        if city:
            city, created = City.objects.get_or_create(name=city)

        if form.is_valid():
            print(request.POST)
            print(request.FILES)

            new_form = form.save(commit=False)
            new_form.city = city
            new_form = form.save()

            if guide:
                messages.success(request, 'Profile has been updated!')
            else:
                messages.success(request, 'Profile has been created!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user_interests = UserInterest.objects.filter(user=user)

    services = Service.objects.all()
    guide_services = GuideService.objects.filter(guide=guide)
    guide_services_ids = [item.service.id for item in guide_services]
    print (guide_services_ids)

    return render(request, 'users/profile_settings_guide.html', locals())


@login_required()
def profile_settings_tourist(request):
    page = "profile_settings_tourist"
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    form = TouristProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        print(request.FILES)


        interests = request.POST.getlist("interests")
        user_interest_list = list()
        if interests:
            for interest in interests:
                interest, created = Interest.objects.get_or_create(name=interest)

                #adding to bulk create list for faster creation all at once
                user_interest_list.append(UserInterest(interest=interest, user=user))


        UserInterest.objects.filter(user=user).delete()
        UserInterest.objects.bulk_create(user_interest_list)

        new_form_profile = form.save(commit=False)
        new_form_profile = form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user_interests = UserInterest.objects.filter(user=user)

    return render(request, 'users/profile_settings_tourist.html', locals())


@login_required()
def general_settings(request):
    page = "general_settings"
    user = request.user
    form = PasswordChangeForm(data=request.POST or None, user=user)
    if request.method == 'POST':

        if form.is_valid():
            new_form = form.save(commit=False)
            new_form = form.save()
            messages.success(request, 'Password was successfully updated!')
            update_session_auth_hash(request, user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'users/general_settings.html', locals())


@login_required()
def profile_overview(request, username=None):
    user = request.user
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponseRedirect(reverse("home"))

    #if no username is specified in url, it is possible to display info just for current user
    elif not user.is_anonymous():
        user = request.user
    else:
        return HttpResponseRedirect(reverse("home"))

    user_profile, created = GuideProfile.objects.get_or_create(user=user)


    return render(request, 'users/profile_overview.html', locals())


def profile_photos(request, username = None):
    user = request.user
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            return HttpResponseRedirect(reverse("home"))

    #if no username is specified in url, it is possible to display info just for current user
    elif not user.is_anonymous():
        user = request.user
    else:
        return HttpResponseRedirect(reverse("home"))

    user_profile, created = UserProfile.objects.get_or_create(user=user)


    if not username:
        my_profile = True

    travel_images = UserTravelImage.objects.filter(user=user)
    form = UserTravelImageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        new_form = form.save(commit=False)
        new_form.user = user
        new_form = form.save()

        messages.success(request, 'New image was successfully added!')

    return render(request, 'new_template/users/profile_photos.html', locals())


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
    if not user.is_anonymous() and user.guideprofile:
        current_role = request.session.get("current_role")
        if current_role == "tourist":
            request.session["current_role"] = "guide"
            messages.success(request, 'Switched to guide profile!')
        else:
            request.session["current_role"] = "tourist"
            messages.success(request, 'Switched to tourist profile!')
    else:
        request.session["current_role"] = "tourist"
        messages.error(request, 'You do not have a guide profile!')

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


@login_required()
def tourist(request, username):
    user = request.user
    tourist = user.profile

    orders = Order.objects.filter(user=user).order_by('-id')
    order_ids = [item.id for item in orders]

    tours_ids = [item.tour.id for item in orders]
    tours = Tour.objects.filter(id__in=tours_ids).order_by("-rating")

    reviews = Review.objects.filter(id__in=order_ids, is_from_tourist=True, is_active=True)

    return render(request, 'users/tourist.html', locals())
