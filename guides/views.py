from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from users.models import Interest, UserInterest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Review


def guides(request):
    current_page = "guides"

    user = request.user

    base_kwargs = dict()
    hourly_price_kwargs = dict()


    filtered_hourly_prices = request.GET.get('hourly_price')
    filtered_cities = request.GET.getlist('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_is_hourly_price_included = request.GET.get('is_hourly_price_included')

    city_input = request.GET.getlist(u'city_input')
    guide_input = request.GET.getlist(u'guide_input')

    order_results = request.GET.get('order_results')

    #for filtering by price type we need to implement 2-levels logic.
    #all other filters except pricing will be based filter and each of 3 types of pricing
    # will be combined with the base filters
    #Hourly price tours filtering
    if filtered_is_hourly_price_included and filtered_hourly_prices:
        price = filtered_hourly_prices.split(";")
        if len(price)==2:
            hourly_price_kwargs["rate__gte"] = price[0]
            hourly_price_kwargs["rate__lte"] = price[1]


    #filtering by cities
    if city_input:
        base_kwargs["city__name__in"] = city_input

    #filtering by guides
    if guide_input:
        base_kwargs["user__username__in"] = guide_input

    print ("guide_input: %s" % guide_input)

    #ordering
    if order_results:
        if order_results == "price":
            order_results = ["rate"]
            order_results = tuple(order_results)

        elif order_results == "-price":
            order_results = ["-rate"]
            order_results = tuple(order_results)

        elif order_results == "rating":
            order_results = tuple(["rating"])

        elif order_results == "-rating":
            order_results = tuple(["-rating"])

        else:
            order_results = tuple(["rate"])

    else:
        order_results = tuple(["rate"])


    #it is needed for displaying of full list of filters
    # even if some filters are not available for the current list of tours

    #if it is one element in tuple, * is not needed

    print (order_results)
    guides_initial = GuideProfile.objects.filter(is_active=True).order_by(*order_results)

    print (base_kwargs)
    if hourly_price_kwargs:
        print (1)
        # guides = guides_initial.filter(**base_kwargs).filter(**hourly_price_kwargs).order_by(*order_results)

        base_kwargs_mixed = base_kwargs.copy()
        base_kwargs_mixed.update(hourly_price_kwargs)

        guides = guides_initial.filter(**base_kwargs_mixed)

    elif city_input or guide_input:
        print (2)
        # guides = guides_initial.filter(**base_kwargs).order_by(*order_results)
        guides = guides_initial.filter(**base_kwargs)

    elif request.GET:
        print (3)
        guides = GuideProfile.objects.none()

    else:
        print (4)
        guides = guides_initial

    items_nmb = guides.count()


    return render(request, 'guides/guides.html', locals())


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

    reviews = Review.objects.filter(order__guide=guide, is_from_tourist=True, is_active=True)

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
        "reviews": reviews,
        "guide_services": guide_services
    }
    return render(request, 'guides/guide.html', locals())


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
