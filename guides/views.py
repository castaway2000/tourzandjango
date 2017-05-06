from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from users.models import Interest, UserInterest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


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


def search_guide(request):
    response_data = dict()
    results = list()

    if request.GET:
        data = request.GET
        username = data.get(u"q")
        guides = GuideProfile.objects.filter(user__username__icontains=username)

        for guide in guides:
            results.append({
                "id": guide.user.username,
                "text": guide.user.username
            })

    response_data = {
        "items": results,
        "more": "false"
    }
    return JsonResponse(response_data, safe=False)
