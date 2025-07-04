from tourzan.settings import ILLEGAL_COUNTRIES

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from .forms import *
from .models import *
from users.models import Interest, UserInterest, UserLanguage, LanguageLevel, GeneralProfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Review
from locations.models import City
from django.contrib import messages
from utils.internalization_wrapper import languages_english
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Max, Min, Sum, Count, Case, When, Q
from utils.payment_rails_auth import PaymentRailsWidget, PaymentRailsAuth
from django.views.decorators.clickjacking import xframe_options_exempt
from users.models import GeneralProfile
import time
import json
from orders.views import making_booking
from allauth.socialaccount.models import SocialApp
from payments.models import Payment
from orders.models import Order
from django.utils.translation import ugettext as _


@xframe_options_exempt
def guides(request):
    current_page = "guides"
    user = request.user
    services = Service.objects.filter(is_active=True).values()
    try:
       is_guide = bool(user.guideprofile)
    except ObjectDoesNotExist:
       is_guide = False
    except AttributeError:
        is_guide = 'Anon'

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

    print(request.GET)
    location_input = request.GET.get("location_search_input")
    is_country = request.GET.get("is_country")

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
    language_list = [languages_english_dict[l] for l in language_input]

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

    #filtering by location
    if location_input and is_country:
        # base_kwargs["city__original_name__in"] = city_input
        try:
            cities = City.objects.filter(country__place_id=place_id)
            cities_ids = [item.id for item in cities]
            base_kwargs["city_id__in"] = cities_ids
            location_from_place_id = location_input
        except:
            pass
    elif place_id:
        # print("place_id %s" % place_id)
        try:
            city = City.objects.get(place_id=place_id)
            # print(city)
            location_from_place_id = city.full_location
        except:
            pass
        base_kwargs["city__place_id"] = place_id


    #filtering by guides
    if guide_input:
        base_kwargs["uuid__in"] = guide_input
        guide = GuideProfile.objects.get(uuid__in=guide_input)
    if interest_input:
        base_user_interests_kwargs["interest__name__in"] = interest_input
        base_user_interests_kwargs["is_active"] = True
    if service_input:
        base_guide_service_kwargs["service__name__in"] = service_input
    # if languages:  # TODO: later n stuff
    #     user.generalprofile.
    #     base_kwargs["user__generalprofile__getlanguages__in"] = language_list
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

    guides_initial = GuideProfile.objects.filter(is_active=True)
    # print("base kwargs")
    if hourly_price_kwargs:
        # guides = guides_initial.filter(**base_kwargs).filter(**hourly_price_kwargs).order_by(*order_results)
        base_kwargs_mixed = base_kwargs.copy()
        base_kwargs_mixed.update(hourly_price_kwargs)
        guides = guides_initial.filter(**base_kwargs_mixed)
    elif place_id or location_input or guide_input:
        guides = guides_initial.filter(**base_kwargs).order_by(*order_results)
    elif request.GET and request.GET.get("ref_id")==False:#there are get parameters
        guides = GuideProfile.objects.none()
    else:
        guides = guides_initial.filter(**base_kwargs).order_by(*order_results)

    if base_user_interests_kwargs:
        user_interests = UserInterest.objects.filter(**base_user_interests_kwargs)
        interests_user_ids = [item["user_id"] for item in user_interests.values()]
        guides = guides.filter(user_id__in=interests_user_ids)

    if base_guide_service_kwargs:
        guide_services = GuideService.objects.filter(**base_guide_service_kwargs)
        guide_services_guides_ids = [item["guide_id"] for item in guide_services.values()]
        guides = guides.filter(id__in=guide_services_guides_ids)

    items_nmb = guides.count()
    guides_rate_info = guides.aggregate(Min("rate"), Max("rate"))
    if not request.session.get("guides_rates_cached"):
        if items_nmb > 0:#guides found more than 0
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
        index = guides.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = paginator.page_range[start_index:end_index]
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

    illegal_country = False
    countries = City.objects.filter(id=guide.city_id).values()
    if countries:
        try:
            country = countries[0]['full_location'].split(',')[-1].strip()
            for i in ILLEGAL_COUNTRIES:
                if i == country:
                    illegal_country = True
                    break
        except:
            pass
    try:
        tourist = user.touristprofile
        current_order = guide.order_set.filter(status_id=1, tourist=tourist).last()
    except:
        pass

    reviews = Review.objects.filter(order__guide=guide, is_tourist_feedback=True)

    guide_services = GuideService.objects.filter(guide=guide)

    now = datetime.datetime.now().date()
    # form = BookingGuideForm(request.POST or None, guide=guide, initial={"guide_id": guide.id, "date": now})
    form = BookingGuideForm(request.POST or None, guide=guide, initial={"guide_id": guide.id})
    if request.POST and form.is_valid():
        return making_booking(request)

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

    guide_answers = GuideAnswer.objects.filter(guide=guide, is_active=True)\
        .order_by("-question__order_priority", "question__id")
    social_app = SocialApp.objects.filter(provider="facebook").last()
    if social_app:
        app_id = social_app.client_id
    if new_view == "new":
        return render(request, 'guides/guide_new2.html', locals())
    elif new_view == "new-old":
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
    #     messages.success(request, 'New interest was successfully created!')
    #
    # # for pictures: http://ashleydw.github.io/lightbox/
    # context = {
    #     'user_profile': user_profile,
    #     'form': form
    # }
    # return render(request, 'users/profile_settings.html', locals())


@login_required(login_url='/accounts/signup/')  # AS: this is for routing after clicking become a guide
def profile_settings_guide(request, guide_creation=True):
    page = "profile_settings_guide"
    user = request.user
    ref_code = user.generalprofile.referral_code
    user_languages = UserLanguage.objects.filter(user=user, is_active=True)
    language_levels = LanguageLevel.objects.all().values()

    # duplication of this peace of code below in POST area - remake it later
    user_language_native = None
    user_language_second = None
    for user_language in user_languages:
        if user_language.level_id == 1 and not user_language_native:
            user_language_native = user_language
        elif user_language_native and user_language_second:
            user_language_third = user_language
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
            user.generalprofile.set_interests_from_list(interests)
        # Languages assigning
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


        place_id = request.POST.get("place_id")
        full_location = request.POST.get("city_search_input")
        if place_id:
            city_original_name = full_location.split(",")[0]#first part - city name
            city, created = City.objects.get_or_create(place_id=place_id,
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
                price = 0 if price == "" else price
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
            gp = GuideProfile.objects.get(user=user)
            gp.is_default_guide = True
            gp.save()
            return HttpResponseRedirect(reverse("profile_settings_guide"))
            # TODO: check this redirection fix. below is the redirect for identity verification.
            # return HttpResponseRedirect(reverse("identity_verification_router"))
        else:
            messages.success(request, 'Profile has been updated!')
    else:
        general_profile = GeneralProfile.objects.get(user=user)
        #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    language_levels = LanguageLevel.objects.all().values()
    user_language_native, user_language_second, user_language_third = user.generalprofile.get_languages()

    user_interests = UserInterest.objects.filter(user=user, is_active=True)
    services = list(Service.objects.all().values())
    guide_services = GuideService.objects.filter(guide=guide)
    guide_services_dict = dict()
    for item in guide_services:
        guide_services_dict[item.service.id] = item

    for service in services:
        if service["id"] in guide_services_dict:
            service["guide_service"] = guide_services_dict[service["id"]]

    tourist_about = str(user.touristprofile.about)
    #PAY attention: if a guide is new - the template with form should be guides/guide_registration.html
    #for tourist it is always one template for new tourists and for editing of tourist profile,
    # which is users/profile_settings_tourist.html
    if creating_guide:
        return render(request, 'guides/guide_registration.html', locals())
    else:
        return render(request, 'users/profile_settings_guide.html', locals())


@login_required
def profile_questions_guide(request):
    user = request.user
    guide = user.guideprofile
    page = "profile_questions_guide"

    if request.POST:
        guide_answers = GuideAnswer.objects.filter(guide=guide, is_active=True).values()
        existing_answers_question_ids = [item["question_id"] for item in guide_answers]

        data = request.POST
        files = request.FILES
        for k, v in data.items():
            if "-" in k:
                field, question_id = k.split("-")
                if field == "answer":
                    question_id = int(question_id)
                    # if guide answer is already exists or if answer is more than 0 symbols
                    if question_id in existing_answers_question_ids or len(v)>0:
                        default_kwargs = {"text": v}
                        file_name = "file-%s" % question_id
                        if file_name in files:
                            image = files.get(file_name)
                            default_kwargs["image"] = image
                        GuideAnswer.objects.update_or_create(question_id=question_id, guide=guide, defaults=default_kwargs)
        messages.success(request, _('Successfully updated!'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    answers = GuideAnswer.objects.filter(guide=guide, is_active=True)
    answers_dict = dict()
    for answer in answers.iterator():
        obj_dict = dict()
        obj_dict["answer"] = answer.text
        obj_dict["image"] = answer.image_small
        obj_dict["answer_object"] = answer
        answers_dict[answer.question.id] = obj_dict

    questions = Question.objects.filter(is_active=True).order_by("id")
    questions_list = list()
    for question in questions.iterator():
        obj_dict = dict()
        obj_dict["id"] = question.id
        obj_dict["text"] = question.get_text_with_city(guide)
        if answers_dict.get(question.id):
            obj_dict.update(answers_dict.get(question.id))
            questions_list.append(obj_dict)
        else:
            if question.is_active:
                questions_list.append(obj_dict)
            else:
                continue #if there is no guide's answer for is_active=False question, it will not be displayed
    return render(request, 'guides/profile_questions_guide.html', locals())


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
    orders_completed = orders.filter(status_id=4)#completed
    orders_pending = orders.filter(status_id=5)  # payment reserved

    # Amount reserved
    orders_pending_aggr = orders_pending.aggregate(amount=Sum("guide_payment"))
    orders_pending_amount = orders_pending_aggr.get("amount") if orders_pending_aggr.get("amount") else 0

    #Completed and not paid
    orders_completed_not_paid_aggr = orders_completed.filter(guide_payout_date__isnull=True).aggregate(amount=Sum("guide_payment"))
    orders_completed_not_paid_amount = orders_completed_not_paid_aggr.get("amount") if orders_completed_not_paid_aggr.get("amount") else 0

    #Completed and paid
    orders_completed_paid_aggr = orders_completed.filter(guide_payout_date__isnull=False).aggregate(amount=Sum("guide_payment"))
    orders_completed_paid_amount = orders_completed_paid_aggr.get("amount") if orders_completed_paid_aggr.get("amount") else 0

    return render(request, 'guides/earnings.html', locals())


def search_service(request):
    print("search_service")
    results = list()

    if request.GET:
        data = request.GET
        print(data)
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
    guide = user.guideprofile
    general_profile = user.generalprofile
    city = user.guideprofile.city_id
    country = City.objects.filter(id=city).values()[0]['full_location'].split(',')[-1].strip()
    illegal_country = True if '*' in ILLEGAL_COUNTRIES[0] else False
    for i in ILLEGAL_COUNTRIES:
        if i == country:
            illegal_country = True
            break
    if not guide.uuid:
        guide.save(force_update=True)#this will populate automatically uuid value if it is empty so far
    payment_rails_url = PaymentRailsWidget(guide=guide).get_widget_url()
    return render(request, 'guides/guide_payouts.html', locals())


def guides_for_clients(request):
    return render(request, 'guides/guides_for_clients.html', locals())


def tours_for_clients(request):
    return render(request, 'guides/tours_for_clients.html', locals())

def get_average_rate(request):
    loc = request.GET.get('location')
    rates = None
    if request.is_ajax():
        try:
            rates = GuideProfile.objects.filter(city__original_name=loc).aggregate(Avg('rate'))
            print(rates)
        except Exception as err:
            print(err)
    rate = {"rates": rates}
    return JsonResponse(rate)

def get_booked_dates(request):
    data = request.GET
    print("guide_uuid")
    guid_uuid = data.get("guide_uuid")
    print(guid_uuid)
    guide = GuideProfile.objects.get(uuid=guid_uuid)
    booked_dates = [
        {
            "date": "2020-01-20",
            "badge": False,
            "classname": "bg-"
        },
    ]
    return_data = {"booked_dates": booked_dates}
    print(return_data)
    return JsonResponse(return_data)