from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from users.models import Interest, UserInterest, UserLanguage, LanguageLevel, GeneralProfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Review
from django.contrib import messages
from utils.internalization_wrapper import languages_english
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Max, Min, Sum
from utils.payment_rails_auth import PaymentRailsWidget, PaymentRailsAuth
from django.views.decorators.clickjacking import xframe_options_exempt
from users.models import GeneralProfile


@xframe_options_exempt
def guides(request):
    current_page = "guides"
    user = request.user
    services = Service.objects.filter(is_active=True).values()

    base_kwargs = dict()
    base_user_interests_kwargs = dict()
    base_guide_service_kwargs = dict()
    hourly_price_kwargs = dict()
    with_company_kwargs = dict()

    filtered_hourly_prices = request.GET.get('hourly_price')

    # Review these 2 variables if they can be deleted, because they are replaced bellow
    filtered_cities = request.GET.getlist('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_is_hourly_price_included = request.GET.get('is_hourly_price_included')

    city_input = request.GET.get(u'city_input')
    place_id = request.GET.get("place_id")
    guide_input = request.GET.getlist(u'guide_input')
    interest_input = request.GET.getlist(u'interest_input')
    service_input = request.GET.getlist(u'service_input')
    language_input = request.GET.getlist(u'language_input')
    is_company = request.GET.get('is_company')
    is_verified = request.GET.get('is_verified')
    filter_form_data = request.GET.get('filter_form_data')

    #a way to filter tuple of tuples
    languages_english_dict = dict(languages_english)
    languages = [(x,languages_english_dict[x]) for x in language_input]

    order_results = request.GET.get('order_results')

    #for filtering by price type we need to implement 2-levels logic.
    #all other filters except pricing will be based filter and each of 3 types of pricing
    # will be combined with the base filters
    #Hourly price tours filtering
    if filtered_hourly_prices:
        hourly_price = filtered_hourly_prices.split(";")
        if len(hourly_price)==2:
            hourly_price_min = hourly_price[0]
            hourly_price_max = hourly_price[1]
            hourly_price_kwargs["rate__gte"] = hourly_price_min
            hourly_price_kwargs["rate__lte"] = hourly_price_max

    #filtering by cities
    if place_id:
        # print("place_id %s" % place_id)
        try:
            city = City.objects.get(place_id=place_id)
            # print(city)
            city_from_place_id = city.full_location
        except:
            pass
        base_kwargs["city__place_id"] = place_id
    elif city_input:
        print(city_input)
        # base_kwargs["city__original_name__in"] = city_input
        try:
            city = City.objects.get(original_name=city_input)
            # print(city)
            city_from_place_id = city.full_location
            place_id = city.place_id
        except:
            pass
        base_kwargs["city__place_id"] = place_id

    # print(base_kwargs)

    #filtering by guides
    if guide_input:
        base_kwargs["uuid__in"] = guide_input
        guide = GuideProfile.objects.get(uuid__in=guide_input)
    if interest_input:
        base_user_interests_kwargs["interest__name__in"] = interest_input
    if service_input:
        base_guide_service_kwargs["service__name__in"] = service_input

    if filter_form_data and not is_company:
        base_kwargs["user__generalprofile__is_company"] = False

    if filter_form_data and is_verified:
        base_kwargs["user__generalprofile__is_verified"] = True
        # pass #show all
    # else:
    #     base_kwargs["user__generalprofile__is_verified"] = True
    # print(request.GET)
    # print(base_kwargs)

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

    guides_initial = GuideProfile.objects.filter(is_active=True).order_by(*order_results)
    # print("base kwargs")
    print (base_kwargs)
    if hourly_price_kwargs:
        # guides = guides_initial.filter(**base_kwargs).filter(**hourly_price_kwargs).order_by(*order_results)
        base_kwargs_mixed = base_kwargs.copy()
        base_kwargs_mixed.update(hourly_price_kwargs)
        guides = guides_initial.filter(**base_kwargs_mixed)
    elif place_id or city_input or guide_input:
        guides = guides_initial.filter(**base_kwargs).order_by(*order_results)
        print(guides)
        # guides = guides_initial.filter(**base_kwargs)
    elif request.GET and request.GET.get("ref_id")==False:#there are get parameters
        guides = GuideProfile.objects.none()
    else:
        guides = guides_initial.filter(**base_kwargs).order_by(*order_results)

    if base_user_interests_kwargs:
        user_interests = UserInterest.objects.filter(**base_user_interests_kwargs)
        interests_user_ids = [item.user.id for item in user_interests]
        guides = guides.filter(user_id__in=interests_user_ids)

    if base_guide_service_kwargs:
        guide_services = GuideService.objects.filter(**base_guide_service_kwargs)
        guide_services_guides_ids = [item.guide.id for item in guide_services]
        guides = guides.filter(id__in=guide_services_guides_ids)

    items_nmb = guides.count()
    guides_rate_info = guides.aggregate(Min("rate"), Max("rate"))
    if not request.session.get("guides_rates_cached"):
        if items_nmb>0:#guides found more than 0
            rate_min = guides_rate_info.get("rate__min", 0)
            rate_max = guides_rate_info.get("rate__max")
        else:
            rate_min = 0
            rate_max = 50#defaulr max value
        request.session["guides_rate_min"] = int(rate_min) if float(rate_min).is_integer() else float(rate_min)
        request.session["guides_rate_max"] = int(rate_max) if float(rate_max).is_integer() else float(rate_max)
        request.session["guides_rates_cached"] = True

    page = request.GET.get('page', 1)
    paginator = Paginator(guides, 10)
    try:
        guides = paginator.page(page)
    except PageNotAnInteger:
        guides = paginator.page(1)
    except EmptyPage:
        guides = paginator.page(paginator.num_pages)

    if request.GET.get("ref_id"):
        return render(request, 'guides/guides_iframe.html', locals())
    else:
        return render(request, 'guides/guides.html', locals())


def guide(request, guide_name=None, general_profile_uuid=None, new_view=None):
    user = request.user
    print("new view %s" % new_view)
    #referal id for partner to track clicks in iframe
    ref_id = request.GET.get("ref_id")
    if ref_id and not "ref_id" in request.session:
        request.session["ref_id"] = ref_id

    if general_profile_uuid:
        try:
            general_profile = GeneralProfile.objects.get(uuid=general_profile_uuid)
            guide_user = general_profile.user
        except:
            return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))

    if not hasattr(guide_user, "guideprofile"):
        return HttpResponseRedirect(reverse("home"))

    guide = guide_user.guideprofile
    tours = guide.tour_set.filter(is_active=True, is_deleted=False)
    tours_nmb = tours.count()

    try:
        tourist = user.touristprofile
        current_order = guide.order_set.filter(status_id=1, tourist=tourist).last()
    except:
        pass

    reviews = Review.objects.filter(order__guide=guide, is_tourist_feedback=True)

    guide_services = GuideService.objects.filter(guide=guide)

    if request.POST:
        data = request.POST
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


    page = request.GET.get('page', 1)
    paginator = Paginator(reviews, 10)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    #it is not used so far
    context = {
        "guide": guide,
        "reviews": reviews,
        "guide_services": guide_services
    }

    guide_answers = GuideAnswer.objects.filter(guide=guide).order_by("order_priority", "id")

    if new_view=="new":
        return render(request, 'guides/guide_new.html', locals())
    else:
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
def profile_settings_guide(request, guide_creation=True):
    print("profile_settings_guide")

    page = "profile_settings_guide"
    user = request.user

    user_languages = UserLanguage.objects.filter(user=user)
    language_levels = LanguageLevel.objects.all().values()

    #dublication of this peace of code below in POST area - remake it later
    user_language_native = None
    for user_language in user_languages:
        if user_language.level_id == 1 and not user_language_native:
            user_language_native = user_language
        else:
            user_language_second = user_language

    try:
        guide = user.guideprofile
        creating_guide = False
    except:
        if request.session.get("guide_registration_welcome_page_seen") != True:
            return HttpResponseRedirect(reverse("guide_registration_welcome"))
        else:
            guide = None
            creating_guide = True

    if guide:
        form = GuideProfileForm(request.POST or None, request.FILES or None, instance=guide)
    else:
        form = GuideProfileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form_data = form.cleaned_data

        #creating or getting general profile to assign to it first_name and last_name
        general_profile, created = GeneralProfile.objects.get_or_create(user=user)
        if request.POST.get("first_name"):
            general_profile.first_name = request.POST.get("first_name")
        if request.POST.get("last_name"):
            general_profile.last_name = request.POST.get("last_name")

        general_profile.date_of_birth = form_data["date_of_birth"]
        general_profile.save(force_update=True)

        #Interests assigning
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
        language_native = request.POST.get("language_native")
        language_second = request.POST.get("language_second")
        language_second_proficiency = request.POST.get("language_second_proficiency")

        if language_native or language_second:
            user_languages_list = list()
            if language_native:
                user_languages_list.append(UserLanguage(language=language_native, user=user,
                                                        level_id=1))
            if language_second:
                user_languages_list.append(UserLanguage(language=language_second, user=user,
                                                        level_id=language_second_proficiency))

            UserLanguage.objects.filter(user=user).delete()
            user_languages = UserLanguage.objects.bulk_create(user_languages_list)

            # duplication of the peace of code at the beginning of the function
            user_language_native = None
            for user_language in user_languages:
                if user_language.level_id == 1 and not user_language_native:
                    user_language_native = user_language
                else:
                    user_language_second = user_language

        place_id = request.POST.get("place_id")
        full_location = request.POST.get("city_search_input")
        if place_id:
            city_original_name = full_location.split(",")[0]#first part - city name
            city, created = City.objects.get_or_create(place_id =place_id ,
                                                       defaults={"full_location": full_location,
                                                                 "original_name": city_original_name})
        new_form = form.save(commit=False)
        if place_id:
            new_form.city = city
        if not guide:
            new_form.user = user
            new_form.is_active = True

        new_form = form.save()

        #saving services
        guide = new_form
        guide_services_ids_list = list()
        for name, value in request.POST.items():
            string_key = "service_"
            if name.startswith(string_key):
                cleared_name = name.partition(string_key)[2]#getting part of the variable name which is field name
                service = Service.objects.get(html_field_name=cleared_name)
                price_field_name = "serviceprice_%s" % cleared_name
                price = request.POST.get(price_field_name, 0)
                guide_service, created = GuideService.objects.update_or_create(service=service, guide=guide,
                                                                               is_active=True, defaults={"price": price})
                guide_services_ids_list.append(guide_service.id)

        GuideService.objects.filter(guide=guide).exclude(id__in=guide_services_ids_list).update(is_active=False)

        if creating_guide:
            #after success registration delete of pending variable which set redirect to Welcome page
            if "guide_registration_welcome_page_seen" in request.session:
                del request.session["guide_registration_welcome_page_seen"]
            request.session["current_role"] = "guide"
            messages.success(request, 'Profile has been created! Please complete identity verification process!')
            return HttpResponseRedirect(reverse("identity_verification_router"))
        else:
            messages.success(request, 'Profile has been updated!')

        #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user_interests = UserInterest.objects.filter(user=user)
    services = Service.objects.all()
    guide_services = GuideService.objects.filter(guide=guide)
    guide_services_ids = [item.service.id for item in guide_services]

    #PAY attention: if a guide is new - the template with form should be guides/guide_registration.html
    #for tourist it is always one template for new tourists and for editing of tourist profile,
    # which is users/profile_settings_tourist.html
    if creating_guide:
        return render(request, 'guides/guide_registration.html', locals())
    else:
        return render(request, 'users/profile_settings_guide.html', locals())


def search_guide(request):
    response_data = dict()
    results = list()

    if request.GET:
        data = request.GET
        username = data.get(u"q")
        guides = GuideProfile.objects.filter(user__first_name__icontains=username, is_active=True)
        for guide in guides:
            results.append({
                "id": guide.uuid,
                "text": guide.user.generalprofile.first_name
            })

    response_data = {
        "items": results,
        "more": "false"
    }
    return JsonResponse(response_data, safe=False)


def guide_registration_welcome(request):
    return render(request, 'guides/guide_registration_welcome.html', locals())


#intermediate view to assign a session variable to those who wants to be a guide
def guide_registration_welcome_confirmation(request):
    request.session["guide_registration_welcome_page_seen"] = True
    return HttpResponseRedirect(reverse("guide_registration"))


def earnings(request):
    user = request.user
    try:
        guide = user.guideprofile

        if request.session.get("current_role") != "guide":
            return HttpResponseRedirect(reverse("home"))

        kwargs = dict()
        kwargs["payment_status_id"] = 4

        if request.GET:
            data = request.GET
            date_start = data.get("date_start")
            date_end = data.get("date_end")
            if date_start:
                kwargs["dt_paid__gte"] = date_start
            if date_end:
                kwargs["dt_paid__lte"] = date_end

        orders = guide.order_set.filter(**kwargs).order_by("-id")
    except:
        return HttpResponseRedirect(reverse("home"))
    return render(request, 'guides/earnings.html', locals())


def search_service(request):
    print ("search_service")
    results = list()

    if request.GET:
        data = request.GET
        print (data)
        service_name = data.get(u"q")
        services = Service.objects.filter(name__icontains=service_name)

        for item in services:
            results.append({
                "id": item.name,
                "text": item.name
            })

    response_data = {
        "items": results,
        "more": "false"
    }

    return JsonResponse(response_data, safe=False)


@login_required()
def guide_payouts(request):
    user = request.user
    try:
        guide = user.guideprofile
        general_profile = user.generalprofile
        if not guide.uuid:
            guide.save(force_update=True)#this will populate automatically uuid value if it is empty so far
        payment_rails_url = PaymentRailsWidget(guide=guide).get_widget_url()
        return render(request, 'guides/guide_payouts.html', locals())
    except:
        messages.error(request, 'You have no permissions for this action!')
        return render(request, 'users/home.html', locals())


def guides_for_clients(request):
    return render(request, 'guides/guides_for_clients.html', locals())


def tours_for_clients(request):
    return render(request, 'guides/tours_for_clients.html', locals())
