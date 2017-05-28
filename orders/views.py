# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from .models import Order, Review
from locations.models import City
from guides.models import GuideProfile
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from tourists.models import TouristProfile
from django.contrib import messages
from tours.models import Tour
from utils.statuses_changing_rules import checking_statuses
import datetime


@login_required()
def making_booking(request):
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
    tour_id = data.get("tour_id")
    guide_id = data.get("guide_id")

    if tour_id:
        tour = Tour.objects.get(id=tour_id)
        guide = tour.guide
        guide_id = guide.id
        kwargs["tour_id"] = tour_id
    else:
        guide = GuideProfile.objects.get(id=guide_id)


    tourist = TouristProfile.objects.get(user=user)

    date_booked_for = data["start"]
    date_booked_for = datetime.strptime(date_booked_for, '%Y, %B %d, %A').date()

    hours_nmb = data.get("booking_hours")
    price_hourly = data.get("price_hourly", 0)

    if price_hourly:
        price_hourly = price_hourly.replace(",", ".")
    elif tour_id:
        if tour.payment_type.id==1:
            price_hourly = 0
        elif tour.payment_type.id == 2:
            kwargs["price"] = tour.price
        else:
            price_hourly = 0
    else:
        price_hourly = guide.rate

    # if hours_nmb and price_hourly:
    #     price = int(hours_nmb)*float(price_hourly)
    # else:
    #     price = data.get("price", 0)
    #     if price:
    #         price = price.replace(",", ".")
    #
    # discount = data.get("discount", 0)
    # if discount:
    #     price_after_discount = price-discount
    # else:
    #     price_after_discount = price
    #
    # if hours_nmb:
    #     kwargs["hours_nmb"] = hours_nmb
    # else:
    #     kwargs["hours_nmb"] = 0

    if price_hourly:
        kwargs["price_hourly"] = price_hourly
    else:
        kwargs["price_hourly"] = 0

    # kwargs["tour_id"] = tour_id
    kwargs["tourist"] = tourist
    kwargs["guide_id"] = guide_id
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
            Order.objects.get_or_create(**kwargs)
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
    # kwargs["user"] = user

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
        kwargs["guide__city__name__in"] = filtered_cities

    if filtered_guides:
        print (filtered_guides)
        kwargs["guide__user__username__in"] = filtered_guides

    if not status:
        print (kwargs)

        initial_orders = Order.objects.filter(tourist__user=user)#it is needed for citieas and guides list
        orders = initial_orders.filter(**kwargs).order_by('-id')
        bookings_nmb = orders.count()
    elif not user.is_anonymous():
        kwargs["status__name"] = status
        initial_orders = Order.objects.filter(tourist__user=user, status__name=status)#it is needed for citieas and guides list
        orders = initial_orders.filter(**kwargs).order_by('-id')
        bookings_nmb = orders.count()
    else:
        current_url = request.path
        url = "/login?next=%s" % current_url
        return HttpResponseRedirect(url)


    cities_ids = [item.guide.city.id for item in initial_orders]
    cities = City.objects.filter(id__in=cities_ids, is_active=True)

    guides_ids = [item.guide.id for item in initial_orders]
    guides = GuideProfile.objects.filter(id__in=guides_ids, is_active=True)

    return render(request, 'orders/bookings.html', locals())


@login_required()
def orders(request, status=None):
    user = request.user

    try:
        guide = user.guideprofile
        data = request.GET

        kwargs = dict()

        tour_id = data.get("tour_id")
        if tour_id:
            kwargs["tour_id"] = tour_id

        if not status:
            kwargs["guide"] = guide
            orders = Order.objects.filter(**kwargs).order_by("-id")
        else:
            kwargs["guide"] = guide
            kwargs["status__slug"] = status
            orders = Order.objects.filter(**kwargs).order_by("-id")

        orders_nmb = orders.count()
        return render(request, 'orders/orders.html', locals())
    except Exception as e:
        print (e)
        messages.error(request, 'You have no permissions for this action!')
        return HttpResponseRedirect(reverse("home"))


@login_required()
def guide_settings_orders(request):
    page = "settings_orders"
    user = request.user
    guide = user.guideprofile
    orders = Order.objects.filter(guide=guide).order_by("-id")
    return render(request, 'orders/profile_settings_guide_orders.html', locals())


@login_required()
def tourist_settings_orders(request):
    page = "settings_orders"
    user = request.user
    tourist = user.touristprofile
    orders = Order.objects.filter(tourist=tourist).order_by("-id")
    return render(request, 'orders/profile_settings_tourist_bookings.html', locals())


@login_required()
def cancel_order(request, order_id):
    user = request.user

    current_role = request.session.get("current_role")
    if current_role == "tourist" or not current_role:
        #check if a user is a tourist in an order
        try:
            tourist = user.touristprofile
            order = Order.objects.get(id=order_id, tourist=tourist)
            order.status_id = 3
            order.save(force_update=True)
            print ("try 2")
            messages.success(request, 'Order has been successfully cancelled!')
        except:
            messages.error(request, 'You have no permissions for this action!')
    else:
        #check if a user is a guide
        try:
            guide = user.guideprofile
            order = Order.objects.get(id=order_id, guide=guide)
            order.status_id = 6
            order.save(force_update=True)
            print ("try 1")
            print (order.status)
            messages.success(request, 'Order has been successfully cancelled!')
        except:
            messages.error(request, 'You have no permissions for this action!')



    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def change_order_status(request, order_id, status_id):
    print ("change order status")
    user = request.user

    current_role = request.session.get("current_role")
    if current_role == "tourist" or not current_role:
        #check if a user is a tourist in an order
        try:
            tourist = user.touristprofile
            order = Order.objects.get(id=order_id, tourist=tourist)

            # checking status transition consistancy for preventing hacking
            checking = checking_statuses(current_status_id=order.status.id, new_status_id=status_id)
            print (checking)
            if checking == False:
                messages.error(request, 'You have no permissions for this action!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            order.status_id = status_id
            order.save(force_update=True)
            messages.success(request, 'Order has been successfully cancelled!')
        except:
            messages.error(request, 'You have no permissions for this action!')
    else:
        #check if a user is a guide
        try:
            guide = user.guideprofile
            order = Order.objects.get(id=order_id, guide=guide)

            # checking status transition consistancy for preventing hacking
            checking = checking_statuses(current_status_id=order.status.id, new_status_id=status_id)
            print (checking)
            if checking == False:
                messages.error(request, 'You have no permissions for this action!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            print ("3")
            print (status_id)
            order.status_id = status_id
            print ("4")
            order.save(force_update=True)
            messages.success(request, 'Order has been successfully cancelled!')
        except Exception as e:
            print (e)
            messages.error(request, 'You have no permissions for this action!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def saving_review(request):
    if request.POST:
        user = request.user
        data = request.POST

        order_id = data.get("order_id")
        name = data.get("title")
        text = data.get("feedback")
        rating = data.get("rating")

        #for adding a possibility to edit a review later
        review_id = data.get("review_id")

        if order_id:
            order = Order.objects.get(id=order_id)

            kwargs = {}
            dt_now = datetime.datetime.utcnow()
            if order.guide.user == user or order.tourist.user == user:
                if order.guide.user == user:
                    guide_kwargs = {
                        "guide_feedback_name": name,
                        "guide_feedback": text,
                        "guide_rating": rating,
                        "is_guide_feedback": True,
                        "guide_review_created": dt_now,
                        "guide_review_updated": dt_now
                    }
                    kwargs = dict(kwargs, **guide_kwargs)
                if order.tourist.user == user:
                    tourist_kwargs = {
                        "tourist_feedback_name": name,
                        "tourist_feedback": text,
                        "tourist_rating": rating,
                        "is_tourist_feedback": True,
                        "tourist_review_created": dt_now,
                        "tourist_review_updated": dt_now
                    }
                    kwargs = dict(kwargs, **tourist_kwargs)
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            Review.objects.update_or_create(order_id=order_id, defaults=kwargs)
            messages.success(request, 'Review has been successfully created!')


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))