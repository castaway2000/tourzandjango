from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from .models import Order
from locations.models import City
from users.models import GuideProfile
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


@login_required()
def tour_booking(request):
    print ("tour bookings123")
    print (request.POST)

    user = request.user
    return_dict = dict()
    if request.POST:
        data = request.POST
    else:
        data = request.GET

    print (data)

    kwargs = dict()
    tour_id = data["tour_id"]
    date_booked_for = data["start"]
    date_booked_for = datetime.strptime(date_booked_for, '%Y, %B %d, %A').date()

    hours_nmb = data.get("booking_hours")
    price_hourly = data.get("price_hourly", 0)
    if price_hourly:
        price_hourly = price_hourly.replace(",", ".")

    if hours_nmb and price_hourly:
        price = int(hours_nmb)*float(price_hourly)
    else:
        price = data.get("price", 0)
        if price:
            price = price.replace(",", ".")

    discount = data.get("discount", 0)
    if discount:
        price_after_discount = price-discount
    else:
        price_after_discount = price

    if hours_nmb:
        kwargs["hours_nmb"] = hours_nmb
    else:
        kwargs["hours_nmb"] = 0

    if price_hourly:
        kwargs["price_hourly"] = price_hourly
    else:
        kwargs["price_hourly"] = 0

    kwargs["tour_id"] = tour_id
    kwargs["user"] = user
    kwargs["price"] = price
    kwargs["discount"] = discount
    kwargs["price_after_discount"] = price_after_discount
    kwargs["date_booked_for"] = date_booked_for

    print (kwargs)

    if user.is_anonymous():
        if "bookings" in request.session:
            request.session["bookings"].append(kwargs)
            return HttpResponseRedirect(reverse("my_bookings"))
        else:
            request.session["bookings"] = []
            request.session["bookings"].append(kwargs)
        return HttpResponseRedirect(reverse("my_bookings"))
    else:
        try:
            Order.objects.create(**kwargs)
        except Exception as e:
            e = e[0]
            text = e.encode('utf-8')
            print (text)

        return_dict["status"] = "success"
        return_dict["message"] = "Request has been submitted! Please waite for confirmation!"

    if request.POST:
        return JsonResponse(return_dict)
    else:
        return HttpResponseRedirect(reverse("my_bookings"))


@login_required
def bookings(request, status=None):
    print ("bookings")
    user = request.user
    kwargs = dict()
    kwargs["user"] = user

    print (request.GET)

    filtered_prices = request.GET.get('price')
    filtered_cities = request.GET.getlist('city')
    filtered_guides = request.GET.getlist('guide')

    if filtered_prices:
        price = filtered_prices.split(";")
        if len(price)==2:

            kwargs["price_after_discount__gte"] = price[0]
            kwargs["price_after_discount__lte"] = price[1]
            print (kwargs)

    if filtered_cities:
        print (filtered_cities)
        kwargs["tour__city__name__in"] = filtered_cities

    if filtered_guides:
        print (filtered_guides)
        kwargs["tour__guide__user__username__in"] = filtered_guides

    if not status:
        initial_orders = Order.objects.filter(user=user)#it is needed for citieas and guides list
        orders = initial_orders.filter(**kwargs).order_by('-id')
        bookings_nmb = orders.count()
    elif not user.is_anonymous():
        kwargs["status__name"] = status
        initial_orders = Order.objects.filter(user=user, status__name=status)#it is needed for citieas and guides list
        orders = initial_orders.filter(**kwargs).order_by('-id')
        bookings_nmb = orders.count()
    else:
        current_url = request.path
        url = "/login?next=%s" % current_url
        return HttpResponseRedirect(url)


    cities_ids = [item.tour.city.id for item in initial_orders]
    cities = City.objects.filter(id__in=cities_ids, is_active=True)

    guides_ids = [item.tour.guide.id for item in initial_orders]
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

    return render(request, 'orders/bookings.html', locals())


def orders(request, status=None):
    user = request.user
    print "orders"
    if not status:
        orders = Order.objects.filter(user=user)
    else:
        orders = Order.objects.filter(status__name=status)
    return render(request, 'orders/orders.html', locals())