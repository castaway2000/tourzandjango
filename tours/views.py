from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Tour
from locations.models import City
from guides.models import GuideProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Review, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _
from django.db.models import Avg, Max, Min, Sum


def tours(request):
    print (request.GET)
    user = request.user

    base_kwargs = dict()
    hourly_price_kwargs = dict()
    fixed_price_kwargs = dict()
    free_price_kwargs = dict()

    filtered_hourly_prices = request.GET.get('hourly_price')
    filtered_fixed_prices = request.GET.get('fixed_price')
    filtered_cities = request.GET.getlist('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_is_hourly_price_included = request.GET.get('is_hourly_price_included')
    filtered_is_fixed_price_included = request.GET.get('is_fixed_price_included')
    filtered_is_free_offers_included = request.GET.get('is_free_offers_included')
    city_input = request.GET.getlist(u'city_input')
    place_id = request.GET.get("place_id")
    guide_input = request.GET.getlist(u'guide_input')
    order_results = request.GET.get('order_results')

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
    if place_id:
        print("place_id %s" % place_id)
        try:
            city = City.objects.get(place_id=place_id)
            print(city)
            city_from_place_id = city.full_location

        except:
            pass
        base_kwargs["city__place_id"] = place_id
    elif city_input:
        base_kwargs["city__name__in"] = city_input

    #filtering by guides
    if guide_input:
        base_kwargs["guide__user__username__in"] = guide_input

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
    tours_initial = Tour.objects.filter(is_active=True, is_deleted=False, guide__is_active=True).order_by(*order_results)
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

        #if it is one element in tuple, * is not needed
        tours = tours_initial.filter(q_objects).order_by(*order_results)
        # print ("12")
        # print (q_objects)
    elif city_input or guide_input:
        # print ("12345")
        tours = tours_initial.filter(**base_kwargs).order_by(*order_results)
    elif request.GET and not "page" in request.GET:
        # print ("15")
        tours = Tour.objects.none()
    else:
        tours = tours_initial

    tours_nmb = tours.count()

    cities_ids = list(set([item.city.id for item in tours_initial]))
    cities = City.objects.filter(id__in=cities_ids, is_active=True)

    guides_ids = list(set([item.guide.id for item in tours_initial ]))
    # print ("guides ids: %s" % guides_ids)
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

    #getting min and max price for prices range slider
    tours_rate_info = tours.aggregate(Min("price"), Max("price"), Min("price_hourly"), Max("price_hourly"))
    if not request.session.get("tours_rates_cached"):
        request.session["tours_rate_fixed_min"] = int(tours_rate_info["price__min"]) if float(tours_rate_info["price__min"]).is_integer() else float(tours_rate_info["price__min"])
        request.session["tours_rate_fixed_max"] = int(tours_rate_info["price__max"]) if float(tours_rate_info["price__max"]).is_integer() else float(tours_rate_info["price__max"])
        request.session["tours_rate_hourly_min"] = int(tours_rate_info["price_hourly__min"]) if float(tours_rate_info["price_hourly__min"]).is_integer() else float(tours_rate_info["price_hourly__min"])
        request.session["tours_rate_hourly_max"] = int(tours_rate_info["price_hourly__max"]) if float(tours_rate_info["price_hourly__max"]).is_integer() else float(tours_rate_info["price_hourly__max"])
        request.session["tours_rates_cached"] = True

    page = request.GET.get('page', 1)
    paginator = Paginator(tours, 5)
    try:
        tours = paginator.page(page)
    except PageNotAnInteger:
        tours = paginator.page(1)
    except EmptyPage:
        tours = paginator.page(paginator.num_pages)

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


def tour(request, slug, tour_id):
    user = request.user

    tour = Tour.objects.get(id=tour_id, slug=slug)
    guide = tour.guide

    try:
        tourist = user.touristprofile
        current_order = Order.objects.filter(tourist=tourist, tour_id=tour_id).last()
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

    return render(request, 'tours/tour.html', locals())


@login_required()
def guide_settings_tours(request):
    page = "settings_tours"
    user = request.user
    tours = Tour.objects.filter(guide=user.guideprofile, is_deleted = False)
    return render(request, 'tours/profile_settings_guide_tours.html', locals())


@login_required()
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

        if request.FILES.get("new_images"):
            for file in request.FILES.getlist("new_images"):
                TourImage.objects.create(image=file, tour=new_form)

        if slug:
            messages.success(request, _('Tour details have been successfully updated!'))
        else:
            messages.success(request, _('Tour details have been successfully created!'))
            return HttpResponseRedirect(reverse("guide_settings_tour_edit", kwargs={"slug": new_form.slug, "tour_id": new_form.id}))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/profile_settings_guide_tour_edit.html', locals())


@login_required()
def deactivate_tour_image(request):
    print (request.POST)
    if request.POST:
        data = request.POST
        tour_id = data.get("tour_id")
        img_id = data.get("img_id")
        TourImage.objects.filter(tour_id=tour_id, id=img_id).update(is_active=False)
    response_date = dict()
    return JsonResponse(response_date)


@login_required()
def make_main_tour_image(request):
    if request.POST:
        data = request.POST
        tour_id = data.get("tour_id")
        img_id = data.get("img_id")
        tour_image = TourImage.objects.get(tour_id=tour_id, id=img_id)
        tour_image.is_main = True
        tour_image.save(force_update=True)
    response_date = dict()
    return JsonResponse(response_date)


@login_required()
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
