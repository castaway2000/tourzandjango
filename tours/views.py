from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Tour
from locations.models import City
from users.models import GuideProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.http import JsonResponse


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

    order_results = request.GET.get("order_results")

    #for filtering by price type we need to implement 2-levels logic.
    #all other filters except pricing will be based filter and each of 3 types of pricing
    # will be combined with the base filters
    #Hourly price tours filtering
    if filtered_is_hourly_price_included and filtered_hourly_prices:
        price = filtered_hourly_prices.split(";")
        if len(price)==2:
            hourly_price_kwargs["price_hourly__gte"] = price[0]
            hourly_price_kwargs["price_hourly__lte"] = price[1]
            hourly_price_kwargs["payment_type_id"] = 1

    #Fixed price tours filtering
    if filtered_is_fixed_price_included and filtered_fixed_prices:
        price = filtered_fixed_prices.split(";")
        if len(price)==2:
            fixed_price_kwargs["price__gte"] = price[0]
            fixed_price_kwargs["price__lte"] = price[1]
            fixed_price_kwargs["payment_type_id"] = 2

    #Free tours filtering
    if filtered_is_free_offers_included:
        free_price_kwargs["is_free"] = True


    if filtered_cities:
        print (filtered_cities)
        base_kwargs["city__name__in"] = filtered_cities

    if filtered_guides:
        print (filtered_guides)
        base_kwargs["guide__user__username__in"] = filtered_guides


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
    else:
        order_results = ("-is_free", "price_hourly")

    #it is needed for displaying of full list of filters
    # even if some filters are not available for the current list of tours

    #if it is one element in tuple, * is not needed
    tours_initial = Tour.objects.filter(is_active=True).order_by(*order_results)


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
    elif request.GET:
        tours = Tour.objects.none()
    else:
        tours = tours_initial

    tours_nmb = tours.count()

    cities_ids = list(set([item.city.id for item in tours_initial]))
    cities = City.objects.filter(id__in=cities_ids, is_active=True)

    guides_ids = list(set([item.guide.id for item in tours_initial]))
    print ("guides ids: %s" % guides_ids)
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

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
    tour = Tour.objects.get(id=tour_id, slug=slug)
    guide = tour.guide
    tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    reviews = tour.review_set.filter(is_active=True)
    other_tours = guide.tour_set.filter(is_active=True).exclude(id=tour.id)
    return render(request, 'tours/tour.html', locals())


@login_required()
def guide_settings_tours(request):
    page = "settings_tours"
    user = request.user
    tours = Tour.objects.filter(guide=user.guideprofile)
    return render(request, 'tours/profile_settings_guide_tours.html', locals())


@login_required()
def guide_settings_tour_edit(request, slug=None, tour_id=None):
    page = "settings_tours"
    user = request.user

    payment_types = PaymentType.objects.all().values("id", "name")
    currencies = Currency.objects.all().values("id", "name")

    if slug and tour_id:
        tour = Tour.objects.get(id=tour_id, slug=slug, guide=user.guideprofile)
        form = TourForm(request.POST or None, request.FILES or None, instance=tour)
        tours_images = tour.tourimage_set.filter(is_active=True).order_by('-is_main', 'id')
    else:
        form = TourForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        print (request.POST)
        data = request.POST

        new_form = form.save(commit=False)

        payment_type = int(data.get(u"payment_type")) if data.get(u"payment_type") else None
        if payment_type == 1:
            print ("hour")

            new_form.currency_id = data.get(u"currency")
            new_form.price_hourly = data.get(u"price_hourly") if data.get(u"price_hourly", 25) else 25
            new_form.min_hours = data.get(u"min_hours") if data.get(u"min_hours") else 2


        elif payment_type == 2:
            print ("fixed")

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
            messages.success(request, 'Tour details have been successfully updated!')
        else:
            messages.success(request, 'Tour details have been successfully created!')
            return HttpResponseRedirect(reverse("guide_settings_tour_edit", kwargs={"slug": new_form.slug}))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'tours/profile_settings_guide_tour_edit.html', locals())


def deactivate_tour_image(request):
    print (request.POST)
    if request.POST:
        data = request.POST
        tour_id = data.get("tour_id")
        img_link = data.get("img_link")
        a = img_link.split("/media/")[1]
        print (a)
        b = TourImage.objects.filter(tour_id=tour_id, image=a).update(is_active=False)
        print (b)
    response_date = dict()
    return JsonResponse(response_date)
