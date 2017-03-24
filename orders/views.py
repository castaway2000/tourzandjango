from django.shortcuts import render, HttpResponseRedirect, reverse
from django.http import JsonResponse
from .models import Order
from locations.models import City
from users.models import GuideProfile
from datetime import datetime
from django.contrib.auth.decorators import login_required


@login_required()
def tour_booking(request):
    print ("tour bookings")

    user = request.user
    return_dict = dict()
    if request.POST:
        data = request.POST
    else:
        data = request.GET

    kwargs = dict()
    tour_id = data["tour_id"]
    date_booked_for = data["start"]
    print (type(date_booked_for))
    date_booked_for = datetime.strptime(date_booked_for, '%Y, %B %d, %A').date()
    # date_booked_for = date_booked_for.date()
    print (type(date_booked_for))

    hours_nmb = data["booking_hours"]
    price_hourly = data.get("price_hourly", 0)
    if price_hourly:
        price = int(hours_nmb)*float(price_hourly)
    else:
        price = data["price"]

    discount = data.get("discount", 0)
    if discount:
        price_after_discount = price-discount
    else:
        price_after_discount = price

    kwargs["hours_nmb"] = hours_nmb
    kwargs["tour_id"] = tour_id
    kwargs["user"] = user
    kwargs["price_hourly"] = price_hourly
    kwargs["price"] = price
    kwargs["discount"] = discount
    kwargs["price_after_discount"] = price_after_discount
    kwargs["date_booked_for"] = date_booked_for

    if user.is_anonymous():
        if "bookings" in request.session:
            request.session["bookings"].append(kwargs)
            return HttpResponseRedirect(reverse("my_bookings"))
        else:
            request.session["bookings"] = []
            request.session["bookings"].append(kwargs)
        return HttpResponseRedirect(reverse("my_bookings"))
    else:
        Order.objects.create(**kwargs)
        return_dict["status"] = "success"
        return_dict["message"] = "Request has been submitted! Please waite for confirmation!"

    if request.POST:
        return JsonResponse(return_dict)
    else:
        return HttpResponseRedirect(reverse("my_bookings"))


@login_required
def bookings(request, status=None):
    user = request.user
    if not status:
        orders = Order.objects.filter(user=user).order_by('-id')
    elif not user.is_anonymous():
        orders = Order.objects.filter(user=user, status__name=status).order_by('-id')
    else:
        current_url = request.path
        print (current_url)

        url = "/login?next=%s" % current_url
        return HttpResponseRedirect(url)

    cities_ids = [item.tour.city.id for item in orders]
    cities = City.objects.filter(id__in=cities_ids, is_active=True)

    guides_ids = [item.tour.guide.id for item in orders]
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

    return render(request, 'orders/bookings.html', locals())


def orders(request, status=None):
    user = request.user
    if not status:
        orders = Order.objects.filter(user=user)
    else:
        orders = Order.objects.filter(status__name=status)
    return render(request, 'orders/orders.html', locals())