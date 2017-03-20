from django.shortcuts import render
from django.http import JsonResponse
from .models import Order
from locations.models import City
from users.models import GuideProfile


# Create your views here.
def tour_booking(request):
    user = request.user
    return_dict = dict()
    if request.POST:
        data = request.POST
        kwargs = dict()

        tour_id = data["tour_id"]
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

        Order.objects.create(**kwargs)
        return_dict["status"] = "success"
        return_dict["message"] = "Request has been submitted! Please waite for confirmation!"

    return JsonResponse(return_dict)


def bookings(request, status=None):
    user = request.user
    if not status:
        orders = Order.objects.filter(user=user)
    else:
        orders = Order.objects.filter(status__name=status)

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