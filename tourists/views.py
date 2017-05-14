from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from users.models import Interest, UserInterest
from orders.models import *
from tours.models import *
from users.models import UserLanguage


@login_required()
def profile_settings_tourist(request):
    page = "profile_settings_tourist"
    user = request.user
    profile, created = TouristProfile.objects.get_or_create(user=user)

    user_languages = UserLanguage.objects.filter(user=user)
    for user_language in user_languages:
        if user_language.level_id == 1:
            user_language_native = user_language
        elif user_language.level_id == 2:
            user_language_second = user_language

    form = TouristProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        print(request.FILES)

        #Interests creation
        interests = request.POST.getlist("interests")
        user_interest_list = list()
        if interests:
            for interest in interests:
                interest, created = Interest.objects.get_or_create(name=interest)

                #adding to bulk create list for faster creation all at once
                user_interest_list.append(UserInterest(interest=interest, user=user))

        UserInterest.objects.filter(user=user).delete()
        UserInterest.objects.bulk_create(user_interest_list)


        #Languages assigning
        language_native = request.POST.get("language_native")
        language_second = request.POST.get("language_second")
        print language_native
        print language_second

        user_languages_list = list()
        user_languages_list.append(UserLanguage(language=language_native, user=user, level_id=1))
        user_languages_list.append(UserLanguage(language=language_second, user=user, level_id=2))

        UserLanguage.objects.filter(user=user).delete()
        UserLanguage.objects.bulk_create(user_languages_list)




        new_form_profile = form.save(commit=False)
        new_form_profile = form.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user_interests = UserInterest.objects.filter(user=user)

    return render(request, 'users/profile_settings_tourist.html', locals())


# @login_required()
# def profile_overview(request, username=None):
#     user = request.user
#     if username:
#         try:
#             user = User.objects.get(username=username)
#         except:
#             return HttpResponseRedirect(reverse("home"))
#
#     #if no username is specified in url, it is possible to display info just for current user
#     elif not user.is_anonymous():
#         user = request.user
#     else:
#         return HttpResponseRedirect(reverse("home"))
#
#     user_profile, created = GuideProfile.objects.get_or_create(user=user)
#
#
#     return render(request, 'users/profile_overview.html', locals())


"""
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
"""


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