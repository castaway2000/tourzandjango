from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import LoginForm
from .models import Profile, GuideProfile
from tours.models import Tour, Review
from locations.models import City
from django.contrib.auth.models import User


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))
            else:
                return HttpResponse("Your is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'users/login_register.html', {})


def logout_view(request):
    user = request.user
    if not user.is_anonymous():
        logout(request)
    return HttpResponseRedirect(reverse("home"))


def home(request):
    current_page = "home"
    guides = GuideProfile.objects.filter(is_active=True)\
        .values("user__first_name", "user__last_name", "user__username", "profile_image", "overview")[:3]

    tours = Tour.objects.filter(is_active=True)
    hourly_tours = tours.filter(payment_type_id=1)[:3]
    fixed_payment_tours = tours.filter(payment_type_id=2)[:3]
    free_tours = tours.filter(is_free=True)[:3]
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

    tours = guide.user.tour_set.filter(is_active=True)
    tours_ids = [tour.id for tour in tours]
    reviews = Review.objects.filter(is_active=True)

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
        "reviews": reviews
    }
    return render(request, 'users/guide.html', context)


def profile_settings(request):
    user = request.user
    if user.is_anonymous():
        return HttpResponseRedirect(reverse("home"))


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
    context = {}
    return render(request, 'users/profile_settings.html', context)


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