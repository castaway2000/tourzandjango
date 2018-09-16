from __future__ import unicode_literals
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from users.models import Interest, UserInterest
from orders.models import *
from tours.models import *
from users.models import UserLanguage, LanguageLevel
from django.contrib import messages
from users.models import GeneralProfile


@login_required()
def profile_settings_tourist(request):
    page = "profile_settings_tourist"
    user = request.user
    ref_code = user.generalprofile.referral_code
    profile, profile_created = TouristProfile.objects.get_or_create(user=user)

    try:
        guide_status = bool(profile.user.guideprofile)
    except:
        guide_status = False

    form = TouristProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():

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

        # Languages assigning
        # it is the same peace of code as at guide view - maybe to remake this in the future
        language_native = request.POST.get("language_native")
        language_second = request.POST.get("language_second")
        language_second_proficiency = request.POST.get("language_second_proficiency") if request.POST.get("language_second_proficiency") != "" else 3
        language_third = request.POST.get("language_third")
        language_third_proficiency = request.POST.get("language_third_proficiency") if request.POST.get("language_third_proficiency") != "" else 3

        if language_native or language_second or language_third:
            user_languages_list = list()
            if language_native:
                user_languages_list.append(UserLanguage(language=language_native, user=user,
                                                        level_id=1))
            if language_second:
                user_languages_list.append(UserLanguage(language=language_second, user=user,
                                                        level_id=language_second_proficiency))
            if language_third:
                user_languages_list.append(UserLanguage(language=language_third, user=user,
                                                        level_id=language_third_proficiency))

            UserLanguage.objects.filter(user=user).delete()
            UserLanguage.objects.bulk_create(user_languages_list)

        new_form_profile = form.save(commit=False)
        new_form_profile = form.save()
        user_interests = UserInterest.objects.filter(user=user)

        #redirect to pending order if tourist account was created
        if request.session.get("pending_order_creation"):
            return HttpResponseRedirect(reverse("making_booking"))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    language_levels = LanguageLevel.objects.all().values()
    user_language_native, user_language_second, user_language_third = user.generalprofile.get_languages()

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
def tourist(request, uuid):
    try:
        general_profile = GeneralProfile.objects.get(uuid=uuid)
        user = general_profile.user
    except:
        return HttpResponseRedirect(reverse("home"))

    tourist = user.touristprofile
    orders = Order.objects.filter(tourist=tourist).order_by('-id')
    tours = tourist.order_set.all().order_by("-id")
    travel_photos = user.touristtravelphoto_set.all().order_by("-id")
    reviews = Review.objects.filter(order__tourist=tourist, is_guide_feedback=True)
    return render(request, 'tourists/tourist.html', locals())


@login_required()
def travel_photos(request):
    page = "profile_travel_photos"
    user = request.user
    profile, created = TouristProfile.objects.get_or_create(user=user)
    travel_photos = user.touristtravelphoto_set.all().order_by("-id")
    form = TouristTravelPhotoForm(request.POST or None, request.FILES or None)

    print(1)
    print(request.FILES.getlist('image'))

    if request.POST and form.is_valid():
        # images = request.FILES.getlist('image')
        # for image in images:
        #     TouristTravelPhoto.objects.create(user=user, image=image)
        new_form = form.save(commit=False)
        new_form.user=user
        new_form = form.save()
        travel_photos = user.touristtravelphoto_set.all().order_by("-id")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tourists/travel_photos.html', locals())


@login_required()
def deleting_travel_photo(request, photo_id):
    user = request.user
    try:
        TouristTravelPhoto.objects.filter(id=photo_id, user=user).delete()
        messages.success(request, 'Successfully deleted!')
    except Exception as e:
        print (e)
        messages.error(request, 'You do not have permissions to perform this action!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
