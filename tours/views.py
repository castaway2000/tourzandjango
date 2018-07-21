from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Tour
from locations.models import City
from guides.models import GuideProfile
from users.models import GeneralProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Review, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.db.models import Avg, Max, Min, Sum
from django.views.decorators.clickjacking import xframe_options_exempt
import datetime
from dateutil.rrule import rrule, DAILY
from orders.views import making_booking


@xframe_options_exempt
def tours(request):
    current_page = "tours"
    user = request.user
    base_kwargs = dict()
    hourly_price_kwargs = dict()
    fixed_price_kwargs = dict()
    free_price_kwargs = dict()
    with_company_kwargs = dict()

    filtered_hourly_prices = request.GET.get('hourly_price')
    filtered_fixed_prices = request.GET.get('fixed_price')
    filtered_cities = request.GET.getlist('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_is_hourly_price_included = request.GET.get('is_hourly_price_included')
    filtered_is_fixed_price_included = request.GET.get('is_fixed_price_included')
    filtered_is_free_offers_included = request.GET.get('is_free_offers_included')
    filtered_is_company = request.GET.get('is_company')
    filtered_is_verified = request.GET.get('is_verified')
    place_id = request.GET.get("place_id")
    guide_input = request.GET.getlist(u'guide_input')
    order_results = request.GET.get('order_results')
    filter_form_data = request.GET.get('filter_form_data')
    location_input = request.GET.get("location_search_input")
    is_country = request.GET.get("is_country")

    #for filtering by price type we need to implement 2-levels logic.
    #all other filters except pricing will be based filter and each of 3 types of pricing
    # will be combined with the base filters
    #Hourly price tours filtering
    if filtered_is_hourly_price_included and filtered_hourly_prices:
        hourly_price = filtered_hourly_prices.split(";")
        if len(hourly_price)==2:
            hourly_price_min = hourly_price[0]
            hourly_price_max = hourly_price[1]
            hourly_price_kwargs["price_hourly__gte"] = hourly_price_min
            hourly_price_kwargs["price_hourly__lte"] = hourly_price_max
            hourly_price_kwargs["payment_type_id"] = 1

    #Fixed price tours filtering
    if filtered_is_fixed_price_included and filtered_fixed_prices:
        fixed_price = filtered_fixed_prices.split(";")
        if len(fixed_price)==2:
            fixed_price_min = fixed_price[0]
            fixed_price_max = fixed_price[1]
            fixed_price_kwargs["price__gte"] = fixed_price_min
            fixed_price_kwargs["price__lte"] = fixed_price_max
            fixed_price_kwargs["payment_type_id"] = 2

    #Free tours filtering
    if filtered_is_free_offers_included:
        free_price_kwargs["is_free"] = True

    #filtering by cities
    if location_input and is_country:
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
            print(city)
            location_from_place_id = city.full_location
        except:
            pass
        base_kwargs["city__place_id"] = place_id


    #filtering by guides
    if guide_input:
        base_kwargs["guide__user__username__in"] = guide_input

    #filtering by company
    if filter_form_data and not filtered_is_company:
        base_kwargs['guide__user__generalprofile__is_company'] = False

    #filtering by trusted guides
    if filter_form_data and not filtered_is_verified:
        pass #show all
    else:
        base_kwargs["guide__user__generalprofile__is_verified"] = True

    # print(base_kwargs)

    # print ("guide_input: %s" % guide_input)
    #ordering
    if order_results:
        if order_results == "price":
            order_results = ["-is_free", "price_hourly"]
            order_results.insert(1, "price")
            order_results = tuple(order_results)
        elif order_results == "-price":
            order_results = ["is_free","-price_hourly"]
            order_results.insert(1, "-price")
            order_results = tuple(order_results)
        elif order_results == "rating":
            order_results = tuple(["rating"])
        elif order_results == "-rating":
            order_results = tuple(["-rating"])
        else:
            order_results = ("-is_free", "price_hourly")
    else:
        order_results = ("-rating", "-is_free", "price_hourly")

    #it is needed for displaying of full list of filters
    # even if some filters are not available for the current list of tours

    #if it is one element in tuple, * is not needed
    # tours_initial = Tour.objects.filter(is_active=True, is_deleted=False, guide__is_active=True).order_by(*order_results)
    tours_initial = Tour.objects.filter(is_active=True, is_deleted=False).order_by(*order_results)
    if hourly_price_kwargs or fixed_price_kwargs or free_price_kwargs:
        """
        #python 2
        z = x.copy()
        z.update(y) # which returns None since it mutates z
        """

        """
        #python 3
        z = {**x, **y}
        """

        # print (base_kwargs)
        q_objects = Q()

        if fixed_price_kwargs:
            fixed_price_filters = base_kwargs.copy()
            fixed_price_filters.update(fixed_price_kwargs)
            q_objects |= Q(**fixed_price_filters)

        if hourly_price_kwargs:
            hourly_price_filters = base_kwargs.copy()
            hourly_price_filters.update(hourly_price_kwargs)
            q_objects |= Q(**hourly_price_filters)

        if free_price_kwargs:
            free_price_filters = base_kwargs.copy()
            free_price_filters.update(free_price_kwargs)
            q_objects |= Q(**free_price_filters)

        #if it is one element in tuple, the second * is not needed
        tours = tours_initial.filter(q_objects).order_by(*order_results)
        # print(tours)

    elif place_id or location_input or guide_input:
        tours = tours_initial.filter(**base_kwargs).order_by(*order_results)

    elif request.GET and not "page" in request.GET and request.GET.get("ref_id")==False:
        # print ("15")
        tours = Tour.objects.none()
    else:
        tours = tours_initial.filter(**base_kwargs).order_by(*order_results)

    tours_nmb = tours.count()
    cities_ids = list(set([item.city.id for item in tours_initial]))
    cities = City.objects.filter(id__in=cities_ids, is_active=True)
    guides_ids = list(set([item.guide.id for item in tours_initial]))
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

    #getting min and max price for prices range slider
    tours_rate_info = tours.aggregate(Min("price"), Max("price"), Min("price_hourly"), Max("price_hourly"))
    if not request.session.get("tours_rates_cached"):
        if tours.count()>0:
            if tours.count() == 1:
                request.session["tours_rate_fixed_min"] = 0
                request.session["tours_rate_fixed_max"] = int(tours_rate_info["price__max"]) if float(tours_rate_info["price__max"]).is_integer() else float(tours_rate_info["price__max"])
                request.session["tours_rate_hourly_min"] = 0
                request.session["tours_rate_hourly_max"] = int(tours_rate_info["price_hourly__max"]) if float(tours_rate_info["price_hourly__max"]).is_integer() else float(tours_rate_info["price_hourly__max"])
            else:
                request.session["tours_rate_fixed_min"] = int(tours_rate_info["price__min"]) if float(tours_rate_info["price__min"]).is_integer() else float(tours_rate_info["price__min"])
                request.session["tours_rate_fixed_max"] = int(tours_rate_info["price__max"]) if float(tours_rate_info["price__max"]).is_integer() else float(tours_rate_info["price__max"])
                request.session["tours_rate_hourly_min"] = int(tours_rate_info["price_hourly__min"]) if float(tours_rate_info["price_hourly__min"]).is_integer() else float(tours_rate_info["price_hourly__min"])
                request.session["tours_rate_hourly_max"] = int(tours_rate_info["price_hourly__max"]) if float(tours_rate_info["price_hourly__max"]).is_integer() else float(tours_rate_info["price_hourly__max"])
        else:
            request.session["tours_rate_fixed_min"] = 0
            request.session["tours_rate_fixed_max"] = 100
            request.session["tours_rate_hourly_min"] = 0
            request.session["tours_rate_hourly_max"] = 50
        request.session["tours_rates_cached"] = True

    page = request.GET.get('page', 1)
    paginator = Paginator(tours, 10)
    try:
        tours = paginator.page(page)
        index = tours.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = paginator.page_range[start_index:end_index]
    except PageNotAnInteger:
        tours = paginator.page(1)
    except EmptyPage:
        tours = paginator.page(paginator.num_pages)

    if request.GET.get("ref_id"):
        return render(request, 'tours/tours_iframe.html', locals())
    else:
        return render(request, 'tours/tours.html', locals())


def guide_tours(request, username):
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

    context = {

    }
    return render(request, 'tours/guide_tours.html', context)

@never_cache
def tour(request, slug, tour_uuid, tour_new=None):
    user = request.user

    #referal id for partner to track clicks in iframe
    ref_id = request.GET.get("ref_id")
    if ref_id and not "ref_id" in request.session:
        request.session["ref_id"] = ref_id

    tour = get_object_or_404(Tour, uuid=tour_uuid, slug=slug)
    guide = tour.guide

    try:
        tourist = user.touristprofile
        current_order = Order.objects.filter(tourist=tourist, tour_id=tour.id).last()
    except:
        pass

    tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    reviews = Review.objects.filter(order__tour=tour, is_tourist_feedback=True)
    reviews_total_nmb = Review.objects.filter(order__tour=tour, is_tourist_feedback=True).count()

    other_tours = guide.tour_set.filter(is_active=True).exclude(id=tour.id)
    other_tours_nmb = other_tours.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(reviews, 10)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    if tour_new == "new":
        if tour.type == "1":
            form = BookingScheduledTourForm(request.POST or None, tour=tour)
        else:
            now = datetime.datetime.now().date()
            form = BookingPrivateTourForm(request.POST or None, tour=tour, initial={"tour_id": tour.id, "date": now})

        if request.method=="POST" and form.is_valid():
            return  making_booking(request)

        return render(request, 'tours/tour_new.html', locals())
    else:
        return render(request, 'tours/tour.html', locals())


@login_required()
@never_cache
def guide_settings_tours(request):
    page = "settings_tours"
    user = request.user
    tours = Tour.objects.filter(guide=user.guideprofile, is_deleted = False)
    return render(request, 'tours/profile_settings_guide_tours.html', locals())


@login_required()
@never_cache
def guide_settings_tour_edit(request, slug=None, tour_id=None):
    page = "settings_tours"
    user = request.user

    payment_types = PaymentType.objects.all().values("id", "name")
    currencies = Currency.objects.all().values("id", "name")

    if slug and tour_id:
        guide = user.guideprofile
        try:
            tour = Tour.objects.get(id=tour_id, slug=slug, guide=guide)
        except:
            tour = Tour.objects.get(id=tour_id, guide=guide)
        form = TourForm(request.POST or None, request.FILES or None, instance=tour)
        tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    else:
        form = TourForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        data = request.POST

        new_form = form.save(commit=False)

        payment_type = int(data.get(u"payment_type")) if data.get(u"payment_type") else None
        if payment_type == 1:

            new_form.currency_id = data.get(u"currency")
            new_form.price_hourly = data.get(u"price_hourly") if data.get(u"price_hourly", 25) else 25
            new_form.min_hours = data.get(u"min_hours") if data.get(u"min_hours") else 2


        elif payment_type == 2:
            new_form.currency_id = data.get(u"currency")
            new_form.price = data.get(u"price") if data.get(u"price") else 50
            new_form.hours = data.get(u"hours") if data.get(u"hours") else 2

        elif payment_type == 3:
            pass

        guide = user.guideprofile
        new_form.guide = guide
        new_form.city = guide.city
        new_form = form.save()

        if request.FILES.get("images"):
            for file in request.FILES.getlist("images"):
                TourImage.objects.create(image=file, tour=new_form)
        if slug:
            messages.success(request, _('Tour details have been successfully updated!'))
        else:
            messages.success(request, _('Tour details have been successfully created!'))
            return HttpResponseRedirect(reverse("guide_settings_tour_edit", kwargs={"slug": new_form.slug, "tour_id": new_form.id}))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/profile_settings_guide_tour_edit_old.html', locals())


@login_required()
@never_cache
def guide_settings_tour_edit_general(request, slug=None):
    page = "tour_edit_general"
    title = _("Tour Edit: General")
    user = request.user

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
        form = TourGeneralForm(request.POST or None, request.FILES or None, instance=tour)
    else:
        form = TourGeneralForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        data = request.POST
        new_form = form.save(commit=False)
        guide = user.guideprofile
        new_form.guide = guide
        new_form.city = guide.city
        new_form.payment_type_id = 2 #fixed type
        new_form = form.save()

        if slug:
            messages.success(request, _('Tour details have been successfully updated!'))
        else:
            messages.success(request, _('Tour details have been successfully created!'))
            return HttpResponseRedirect(reverse("tour_edit_general", kwargs={"slug": new_form.slug }))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/profile_settings_guide_tour_edit_general.html', locals())

@login_required()
def delete_program_tour_item(request, id):
    user = request.user
    guide = user.guideprofile
    if TourProgramItem.objects.filter(id=id, tour__guide=guide).exists():
        TourProgramItem.objects.filter(id=id, tour__guide=guide).update(is_active=False)
        messages.success(request, _('Tour program has been successfully removed!'))
    else:
        messages.success(request, _('You do not have permissions to edit this item!'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
@never_cache
def guide_settings_tour_edit_program(request, slug=None):
    page = "tour_edit_program"
    title = _("Tour Edit: Program")
    user = request.user
    form = TourProgramItemForm(request.POST or None, request.FILES or None)

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    if request.method == 'POST' and form.is_valid():
        data = request.POST.copy().dict()
        program_item_id = data.get("program_item_id")
        image = request.FILES.get("image")
        fields_to_delete = ["program_item_id", "csrfmiddlewaretoken"]
        for field in fields_to_delete:
            if field in data:
                del data[field]
        if image:
            data["image"] = image
        else:
            del data["image"]

        data["tour_id"] = tour.id
        data["time"] = datetime.datetime.strptime(data["time"], "%H:%M")
        data["day"] = 1

        if program_item_id:
            TourProgramItem.objects.update_or_create(id=program_item_id, defaults=data)
            messages.success(request, _('Tour program has been successfully updated!'))
        else:
            TourProgramItem.objects.create(**data)
            messages.success(request, _('Tour program has been successfully updated!'))

    tour_items = tour.get_tourprogram_items()
    return render(request, 'tours/tour_edit_program.html', locals())


@login_required()
@never_cache
def guide_settings_tour_edit_images(request, slug=None):
    page = "tour_edit_images"
    title = _("Tour Edit: Images")
    user = request.user

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
        tour_items = tour.get_tourprogram_items()
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    if request.method == 'POST':
        print("method post")
        if request.FILES.get("images"):
            print(request.FILES.getlist("images"))
            for file in request.FILES.getlist("images"):
                TourImage.objects.get_or_create(image=file, tour=tour)

        messages.success(request, _('Images have been successfully updated!'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    return render(request, 'tours/profile_settings_guide_tour_edit_images.html', locals())


@login_required()
@never_cache
def tour_edit_price(request, slug):
    #for private tours
    page = "tour_edit_price"
    title = _("Tour Edit: Price")
    user = request.user

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
        if tour.type == "1":
            return HttpResponseRedirect(reverse("tour_edit_general"))
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    form = PrivateTourPriceForm(request.POST or None, instance=tour)
    if request.method == 'POST':
        new_form = form.save(commit=False)
        new_form.save()
        messages.success(request, _("Successfully updated!"))
    return render(request, 'tours/tour_edit_price.html', locals())


@login_required()
@never_cache
def available_tour_dates_template(request, slug):
    page = "tour_edit_price_and_schedule"
    title = _("Tour Edit: Price and Schedule")
    user = request.user
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
        tour_items = tour.get_tourprogram_items()
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    scheduled_template_item = ScheduleTemplateItem.objects.filter(tour=tour, is_general_template=True).last()
    print(scheduled_template_item)
    if scheduled_template_item:
        form = TourWeeklyScheduleForm(request.POST or None, instance=scheduled_template_item)
    else:
        form = TourWeeklyScheduleForm(request.POST or None)
    if request.method=="POST":
        data = request.POST.copy()
        print(data)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.is_general_template = True
            new_form.tour = tour
            new_form.save()
            print(new_form.id)
            if "quick-template" in data:
                scheduled_template_item = ScheduleTemplateItem.objects.get(id=new_form.id)
                scheduled_template_item.populate_weekdays()

        scheduled_template_items_dict = dict()
        fields = ["time_start", "price", "seats_total"]
        if "btn_save_template_items" in data:
            for k, v in data.items():
                for field in fields:
                    if field in k:
                        item_id = k.split("-")[1]
                        item_value = v
                        if item_id not in scheduled_template_items_dict:
                            scheduled_template_items_dict[item_id] = dict()
                        if field == "time_start":
                            item_value = datetime.datetime.strptime(item_value, "%H:%M")
                        scheduled_template_items_dict[item_id][field] = item_value

        for item_id, values_dict in scheduled_template_items_dict.items():
            ScheduleTemplateItem.objects.update_or_create(id=item_id, defaults=values_dict)

    weekly_template_items = ScheduleTemplateItem.objects\
        .filter(tour=tour, is_general_template=False, is_active=True)\
        .order_by("day")
    return render(request, 'tours/tour_schedule_weekly_template.html', locals())


@login_required()
def manage_weekly_template_item(request):
    response_dict = dict()
    user = request.user
    if request.POST:
        if hasattr(user, "guideprofile"):
            guide = user.guideprofile
            data = request.POST
            print(data)
            id = data.get("id")
            is_delete = data.get("is_delete")
            if id and is_delete:
                if ScheduleTemplateItem.objects.filter(id=id, tour__guide=guide).exists():
                    ScheduleTemplateItem.objects.filter(id=id, tour__guide=guide).update(is_active=False)
                    response_dict["status"] = "success"
                else:
                    response_dict["status"] = "error"
            else:
                days_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                new_item_dict = dict()
                new_item_dict["tour_id"] = data["tour_id"]
                fields = ["time_start", "price", "seats_total", "day"]
                for field in fields:
                    new_item_dict[field] = data.get(field)
                    if field == "day":
                        new_item_dict[field] = days_list.index(new_item_dict[field])
                    if field == "time_start":
                        new_item_dict[field] = datetime.datetime.strptime(new_item_dict[field], "%H:%M")
                new_scheduled_item = ScheduleTemplateItem.objects.create(**new_item_dict)
                response_dict["id"] = new_scheduled_item.id
                response_dict.update(new_item_dict)
                response_dict["status"] = "success"
    print(response_dict)
    return JsonResponse(response_dict)


@login_required()
@never_cache
def apply_week_template_to_dates(request, slug):
    page = "tour_edit_price_and_schedule"
    title = _("Tour Edit: Price and Schedule")
    user = request.user
    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    form = WeeklyTemplateApplyForm(request.POST or None)
    if request.POST and form.is_valid():
        data = form.cleaned_data
        date_from = data["date_from"]
        date_to = data["date_to"]
        template_items = tour.get_template_items()
        print(template_items)
        created_items_nmb = 0
        existed_items_nmb = 0
        for date_item in rrule(DAILY, dtstart=date_from, until=date_to):
            weekday_index = date_item.weekday()
            print(weekday_index)
            template_items_to_populate = template_items.get(weekday_index)
            print(template_items_to_populate)
            if template_items_to_populate:
                for item in template_items_to_populate:
                    date_item_with_time = datetime.datetime.combine(date_item, item.time_start)
                    scheduled_tour, created = ScheduledTour.objects.get_or_create(tour=tour, dt=date_item_with_time, defaults={
                        "time_start": item.time_start,
                        "price": item.price,
                        "seats_total": item.seats_total
                    })
                    if created:
                        created_items_nmb += 1
                    else:
                        existed_items_nmb += 1

            messages.success(request, 'Scheduled tours created: %s' % created_items_nmb)

    return render(request, 'tours/apply_week_template_to_dates.html', locals())


@login_required()
@never_cache
def guide_settings_tour_edit_price_and_schedule(request, slug):
    page = "tour_edit_price_and_schedule"
    title = _("Tour Edit: Price and Schedule")
    user = request.user

    if slug:
        guide = user.guideprofile
        tour = get_object_or_404(Tour, slug=slug, guide=guide)
    else:
        return HttpResponseRedirect(reverse("tour_edit_general"))

    now = datetime.datetime.now()
    time_start = datetime.datetime.strptime("09:00", "%H:%M")
    form = TourWeeklyScheduleForm(request.POST or None, initial={"dt": now, "time_start": time_start, "seats_total": 10, "price": "20"})
    if request.method == 'POST' and form.is_valid():
        new_form = form.save(commit=False)
        new_form.tour = tour
        new_form.save()
        messages.success(request, _("Successfully created!"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/tour_edit_price_and_schedule.html', locals())


@login_required()
@never_cache
def tour_edit_scheduled_tour(request, slug, uuid):
    page = "tour_edit_price_and_schedule"
    title = _("Schedule tour editing")
    user = request.user
    if uuid:
        guide = user.guideprofile
        scheduled_tour = get_object_or_404(ScheduledTour, uuid=uuid, tour__guide=guide)
    else:
        messages.error(request, _('You do not have permissions to access this item!'))
        return HttpResponseRedirect(reverse("guide_settings_tours"))

    if not scheduled_tour.has_pending_reserved_bookings():
        form = TourWeeklyScheduleForm(request.POST or None, instance=scheduled_tour)
        if request.method == 'POST' and form.is_valid():
            new_form = form.save(commit=False)
            new_form.save()
            messages.success(request, _("Successfully updated!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/tour_edit_scheduled_tour.html', locals())


@login_required()
def scheduled_tour_delete(request, uuid):
    user = request.user
    if uuid:
        guide = user.guideprofile
        scheduled_tour = get_object_or_404(ScheduledTour, uuid=uuid, tour__guide=guide)
        if scheduled_tour.has_pending_reserved_bookings():
            messages.error(request, _('This tour date has active booking and can not be deleted!'))
        else:
            ScheduledTour.objects.filter(id=scheduled_tour.id).delete()
            messages.success(request, _('Successfully deleted!'))
    else:
        messages.error(request, _('You do not have permissions to access this item!'))
        return HttpResponseRedirect(reverse("tour_edit_general"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
@never_cache
def deactivate_tour_image(request):
    print(request.POST)
    if request.POST:
        data = request.POST
        tour_id = data.get("tour_id")
        img_id = data.get("img_id")
        TourImage.objects.filter(tour_id=tour_id, id=img_id).update(is_active=False)
    response_data = dict()
    return JsonResponse(response_data)


@login_required()
@never_cache
def make_main_tour_image(request):
    if request.POST:
        data = request.POST
        tour_id = data.get("tour_id")
        img_id = data.get("img_id")
        tour_image = TourImage.objects.get(tour_id=tour_id, id=img_id)
        tour_image.is_main = True
        tour_image.save(force_update=True)
    response_data = dict()
    return JsonResponse(response_data)


@login_required()
@never_cache
def tour_deleting(request, tour_id):
    user = request.user
    try:
        tour_for_delete = Tour.objects.get(id=tour_id, guide__user=user)
        tour_for_delete.is_deleted = True
        tour_for_delete.save(force_update=True)
        messages.success(request, 'Tour has been successfully deleted!')
    except:
        messages.success(request, 'You have no permissions for this action!')
    return HttpResponseRedirect(reverse("guide_settings_tours"))