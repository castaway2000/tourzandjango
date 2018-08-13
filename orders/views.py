# -*- coding: utf-8 -*-
from collections import defaultdict
from django.template.defaulttags import register
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse
from .models import Order, Review, ServiceInOrder, OrderStatus, PaymentStatus
from guides.models import GuideProfile
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from tourists.models import TouristProfile
from django.contrib import messages
from tours.models import Tour, ScheduledTour
from utils.statuses_changing_rules import checking_statuses
import datetime
from guides.models import GuideService
from payments.models import PaymentMethod
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRIVATE_KEY, ILLEGAL_COUNTRIES, ON_PRODUCTION
import braintree
from partners.models import Partner
from guides_calendar.models import CalendarItemGuide, CalendarItem
from django.utils.translation import ugettext as _
import time
from django.db.models import Q
from chats.models import Chat
from locations.models import City


if ON_PRODUCTION:
    braintree.Configuration.configure(braintree.Environment.Production,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )
else:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )


#this view is both for booking guides and tours
def making_booking(request):
    # print ("tour bookings123")
    # print (request.POST)
    # print (request.GET)
    user = request.user
    #this code is used instead of login_required decorator to make it
    if user.is_anonymous():
        data = request.POST
        request.session["pending_order_creation"] = data
        # request.session["pending_order_creation"] = dict(request.POST.lists())
        return HttpResponseRedirect(reverse("login"))

    return_dict = dict()
    if request.session.get("pending_order_creation"):
        data_mod = request.session.get("pending_order_creation")
        del request.session["pending_order_creation"]
    elif request.POST:
        data = request.POST
        data_mod = data.dict()
    else:
        data = request.GET
        data_mod = data.dict()

    response_obj = Order().create_order(user_id=user.id, **data_mod)
    status = response_obj["status"]
    redirect = response_obj["redirect"]
    message = response_obj["message"]
    if status == "success":
        messages.success(request, message)
    else:
        messages.error(request, message)

    if redirect == "current_page":
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(redirect)


@login_required
def bookings(request, status=None):
    print("bookings")
    current_page = "bookings"
    statuses = OrderStatus.objects.filter(is_active=True).values("name")
    user = request.user
    kwargs = dict()

    filtered_prices = request.GET.get('price')
    filtered_city = request.GET.get('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_statuses = request.GET.getlist('status_input')

    place_id = request.GET.get("place_id")

    if filtered_prices:
        price = filtered_prices.split(";")
        if len(price) == 2:
            kwargs["price_after_discount__gte"] = price[0]
            kwargs["price_after_discount__lte"] = price[1]
            # print (kwargs)

    # #filtering by cities
    if place_id:
        # print("place_id %s" % place_id)
        try:
            city = City.objects.get(place_id=place_id)
            print(city)
            city_from_place_id = city.full_location #this is inserted to the location search input
        except:
            pass
        kwargs["guide__city__place_id"] = place_id
    elif filtered_city:
        # kwargs["guide__city__original_name"] = filtered_city
        try:
            city = City.objects.get(original_name=filtered_city)
            # print(city)
            city_from_place_id = city.full_location
            place_id = city.place_id
        except:
            pass
        kwargs["guide__city__place_id"] = place_id


    if filtered_guides:
        print(filtered_guides)
        kwargs["guide__user__username__in"] = filtered_guides

    if filtered_statuses and len(filtered_statuses[0])>1:#to handle empty imputs
        kwargs["status__name__in"] = filtered_statuses

    orders_to_exclude = Order.objects.filter(Q(tour__type="1", status_id=1)|Q(tour__isnull=True, status_id=1))
    orders_to_exclude_ids = [item.id for item in orders_to_exclude.iterator()]
    if not status:
        # print (kwargs)
        initial_orders = Order.objects.filter(tourist__user=user)#it is needed for citieas and guides list
        # orders = initial_orders.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
        orders = initial_orders.filter(**kwargs).order_by('-id')
        bookings_nmb = orders.count()
        # print(kwargs)
        # print (orders)

    elif not user.is_anonymous():
        kwargs["status__name"] = status
        initial_orders = Order.objects.filter(tourist__user=user, status__name=status)#it is needed for citieas and guides list
        # orders = initial_orders.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
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

    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'orders/bookings.html', locals())


@login_required()
def orders(request, status=None):
    current_page = "orders"
    statuses = OrderStatus.objects.filter(is_active=True).values("name")

    user = request.user

    try:
        guide = user.guideprofile
        data = request.GET
        filtered_statuses = request.GET.getlist('status_input')

        kwargs = dict()

        if data.get("uuid"):
            kwargs["uuid"] = data.get("uuid")

        if filtered_statuses:
            kwargs["status__name__in"] = filtered_statuses

        tour_id = data.get("tour_id")
        if tour_id:
            kwargs["tour_id"] = tour_id

        orders_to_exclude = Order.objects.filter(Q(tour__type="1", status_id=1)|Q(tour__isnull=True, status_id=1))
        orders_to_exclude_ids = [item.id for item in orders_to_exclude.iterator()]
        if not status:
            kwargs["guide"] = guide
            # print("kwargs %s" % kwargs)
            # orders = Order.objects.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
            orders = Order.objects.filter(**kwargs).order_by('-id')
            # print("not status")
        else:
            kwargs["guide"] = guide
            kwargs["status__slug"] = status
            # orders = Order.objects.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
            orders = Order.objects.filter(**kwargs).order_by('-id')
        orders_nmb = orders.count()

        page = request.GET.get('page', 1)
        paginator = Paginator(orders, 10)
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        return render(request, 'orders/orders.html', locals())
    except Exception as e:
        print(e)
        messages.error(request, 'You have no permissions for this action!')
        return HttpResponseRedirect(reverse("home"))


@login_required()
def guide_settings_orders(request):
    page = "settings_orders"
    user = request.user
    guide = user.guideprofile
    data = request.GET
    order_id = data.get("id")
    is_fee_free = user.generalprofile.is_fee_free
    if guide:
        if order_id:
            if Order.objects.filter(id=order_id, guide=guide).exclude(status_id=1).exists():
                orders = Order.objects.filter(id=order_id, guide=guide).exclude(status_id=1)
            else:
                orders = Order.objects.filter(guide=guide).exclude(status_id=1).order_by("-id")
        else:
            orders = Order.objects.filter(guide=guide).exclude(status_id=1).order_by("-id")
    else:
        return HttpResponseRedirect(reverse("home"))

    return render(request, 'orders/profile_settings_guide_orders.html', locals())


@login_required()
def tourist_settings_orders(request):
    page = "settings_orders"
    user = request.user
    tourist = user.touristprofile
    orders = Order.objects.filter(tourist=tourist).order_by("-id")
    return render(request, 'orders/profile_settings_tourist_bookings.html', locals())


@login_required()
def cancel_order(request, order_uuid):
    user = request.user
    current_role = request.session.get("current_role")
    order = Order.objects.get(uuid=order_uuid)

    if current_role == "tourist" or not current_role:
        status_id = 3 #canceled by tourist
    else:
        status_id = 6 #canceled by guide
    response_data = order.change_status(user.id, current_role, status_id)
    status = response_data["status"]
    message = response_data["message"]
    if status == "success":
        messages.success(request, message)
    else:
        messages.error(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def change_order_status(request, order_uuid, status_id):
    print("change order status")
    user = request.user
    current_role = request.session.get("current_role")
    order = Order.objects.get(uuid=order_uuid)
    response_data = order.change_status(user.id, current_role, status_id)
    status = response_data["status"]
    message = response_data["message"]
    if status == "success":
        messages.success(request, message)
    else:
        messages.error(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
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
                        "guide_feedback_text": text,
                        "guide_rating": rating,
                        "is_guide_feedback": True,
                        "guide_review_created": dt_now,
                        "guide_review_updated": dt_now
                    }
                    kwargs = dict(kwargs, **guide_kwargs)
                if order.tourist.user == user:
                    tourist_kwargs = {
                        "tourist_feedback_name": name,
                        "tourist_feedback_text": text,
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


@login_required()
def order_completing(request, order_uuid):
    user = request.user
    current_role = request.session.get("current_role")

    order = Order.objects.get(uuid=order_uuid)
    services_in_order = order.serviceinorder_set.filter()

    if order.guide.user == user:
        is_guide = True
    if order.tourist.user == user:
        is_tourist = True

    if request.POST:
        data = request.POST

        name = data.get("title")
        text = data.get("feedback")
        rating = data.get("rating")

        kwargs = {}
        dt_now = datetime.datetime.now()
        if order.guide.user == user or order.tourist.user == user:

            if order.guide.user == user and current_role == "guide":
                guide_kwargs = {
                    "guide_feedback_name": name,
                    "guide_feedback_text": text,
                    "guide_rating": rating,
                    "is_guide_feedback": True,
                    "guide_review_created": dt_now,
                    "guide_review_updated": dt_now
                }
                kwargs = dict(kwargs, **guide_kwargs)

                order.status_id = 4 #completed
                order.save(force_update=True)
                Review.objects.update_or_create(order=order, defaults=kwargs)
                messages.success(request, 'Review has been successfully created!')
                # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if order.tourist.user == user and (current_role == "tourist" or not current_role):
                tourist_kwargs = {
                    "tourist_feedback_name": name,
                    "tourist_feedback_text": text,
                    "tourist_rating": rating,
                    "is_tourist_feedback": True,
                    "tourist_review_created": dt_now,
                    "tourist_review_updated": dt_now
                }
                kwargs = dict(kwargs, **tourist_kwargs)

                #completing payment

                response = order.make_payment(user.id)
                message = response["message"]
                if response["status"] == "success":
                    messages.success(request, message)
                    Review.objects.update_or_create(order=order, defaults=kwargs)
                    order = Order.objects.get(uuid=order_uuid)
                elif response["status"] == "error":
                    messages.error(request, message)

        else:
            messages.error(request, _('You do not have permissions to access to this page!'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    return render(request, 'orders/order_completing.html', locals())