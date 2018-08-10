# -*- coding: utf-8 -*-
from collections import defaultdict
from django.template.defaulttags import register
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse
from .models import Order, Review, ServiceInOrder, OrderStatus, PaymentStatus
from locations.models import City
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
        data = request.session.get("pending_order_creation")
        del request.session["pending_order_creation"]
    elif request.POST:
        data = request.POST
    else:
        data = request.GET

    kwargs = dict()
    tour_id = data.get("tour_id")
    guide_id = data.get("guide_id")
    tour_scheduled = data.get("tour_scheduled")

    #ADD HERE MINIMUM HOURS REQUIREMENETS CHECKING
    tour = None
    if tour_id:
        tour = Tour.objects.get(id=tour_id)
        guide = tour.guide
        kwargs["tour"] = tour
        kwargs["guide"] = guide
        if data.get("start"):
            date_booked_for = data.get("start")
        else:
            date_booked_for = data.get("date")
    elif tour_scheduled:
        tour_scheduled = ScheduledTour.objects.get(id=tour_scheduled)
        tour = tour_scheduled.tour
        guide = tour.guide
        kwargs["tour_scheduled"] = tour_scheduled
        kwargs["tour"] = tour
        kwargs["guide"] = guide
        date_booked_for = tour_scheduled.dt
    else:
        guide = GuideProfile.objects.get(id=guide_id)
        if data.get("start"):
            date_booked_for = data.get("start")
        else:
            date_booked_for = data.get("date")
        kwargs["guide"] = guide

    #creating booked time slots in guide's schedule
    #if some of selected time slots is already booked or unavailable - return an error
    time_slots_chosen = None
    if not tour and guide.is_use_calendar and data.get("time_slots_chosen"):
        time_slots_chosen = data.get("time_slots_chosen").split(",")#workaround to conver string to list. ToDo: improve jQuery to sent list
        is_unavailable_or_booked_timeslot = CalendarItemGuide.objects.filter(id__in=time_slots_chosen, status_id__in=[1, 3]).exists()
        if is_unavailable_or_booked_timeslot == True:
            messages.error(request, _('Some selected time slots are not available anymore!'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if not isinstance(date_booked_for, datetime.datetime):
        try:
            date_booked_for = datetime.datetime.strptime(date_booked_for, '%Y, %B %d, %A')
        except:
            try:
                date_booked_for = datetime.datetime.strptime(date_booked_for, '%m.%d.%Y')
            except:
                try:
                    date_booked_for = datetime.datetime.strptime(date_booked_for, '%m/%d/%Y')
                except:
                    date_booked_for = datetime.datetime.strptime(date_booked_for, '%m/%d/%Y %H:%M')
    kwargs["date_booked_for"] = date_booked_for

    # hours_nmb = data.get("booking_hours", 0)
    hours_nmb = data.get("hours", 0)
    kwargs["hours_nmb"] = hours_nmb

    number_people = int(data.get("number_people", 0))
    kwargs["number_persons"] = number_people

    tourist = TouristProfile.objects.get(user=user)
    kwargs["tourist"] = tourist

    if user.is_anonymous():
        print('anon my dude')
        if "bookings" in request.session:
            request.session["bookings"].append(kwargs)
            return HttpResponseRedirect(reverse("my_bookings"))
        else:
            request.session["bookings"] = []
            request.session["bookings"].append(kwargs)
        return HttpResponseRedirect(reverse("my_bookings"))
    else:
        order = Order.objects.create(**kwargs)

        try:#maybe to delete this at all
            services_ids = data.getlist("additional_services_select[]", data.getlist("additional_services_select"))
            # print ("services ids: %s" % services_ids)
            guide_services = GuideService.objects.filter(id__in=services_ids)

            services_in_order=[]
            additional_services_price = float(0)
            for guide_service in guide_services:
                additional_services_price += float(guide_service.price)
                service_in_order = ServiceInOrder(order_id=order.id, service=guide_service.service,
                                                  price=guide_service.price, price_after_discount=guide_service.price)
                services_in_order.append(service_in_order)

            ServiceInOrder.objects.bulk_create(services_in_order)
            order.additional_services_price = additional_services_price
        except:
            pass

        order.save(force_update=True)
        print('SUCCESS!! >> ', order)

        return_dict["status"] = "success"
        return_dict["message"] = "Request has been submitted! Please wait for confirmation!"

    if time_slots_chosen:#no time slots for tours with fixed price
        for time_slot_chosen in time_slots_chosen:
            #get or update functionality, but without applying for booked items
            # print ("try")
            # print(time_slot_chosen)
            calendar_item_guide = CalendarItemGuide.objects.get(id=time_slot_chosen, guide=guide)
            # print(calendar_item_guide.id)
            # print(calendar_item_guide.calendar_item)
            if calendar_item_guide.status_id == 2: #available
                calendar_item_guide.status_id = 1 #booked
                calendar_item_guide.order = order
                calendar_item_guide.save(force_update=True)

    country = City.objects.filter(id=guide.city_id).values()[0]['full_location'].split(',')[-1].strip()
    illegal_country = False
    for i in ILLEGAL_COUNTRIES:
        if i == country:
            illegal_country = True
            break
    #got rid of returning data for ajax calls

    if (order.tour and order.tour.type == "2") or not order.tour:#private tours and guide booking leads to chat page
        print(11)
        topic = "Chat with %s" % guide.user.generalprofile.first_name
        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user, order=order,
                                                   defaults={"topic": topic})
        initial_message = data.get("message")

        #message about creation of the order
        if order.tour:
            message = _("Tour: {tour_name} \n"
                        "Persons number: {persons_nmb}\n"
                        "Date: {tour_date}".format(tour_name=tour.name,
                                                     persons_nmb=order.number_persons,
                                                     tour_date=order.date_booked_for
                                                     ))
        else:
             message = _("Guide booking request\n"
                        "Persons number: {persons_nmb}\n"
                        "Date: {tour_date}".format(persons_nmb=order.number_persons,
                                                     tour_date=order.date_booked_for
                                                     ))
        chat.create_message(user, message)

        #initial message of the user
        if initial_message:
            chat.create_message(user, initial_message)

        messages.success(request, _("We have successfully sent your request to a guide. "))
        # messages.success(request, _("We have successfully sent your request to a guide. "
        #                             "You will receive email confirmation of the tour by emails soon"))
        return HttpResponseRedirect(reverse("livechat_room", kwargs={"chat_uuid": chat.uuid} ))

    else:
        return HttpResponseRedirect(reverse("order_payment_checkout", kwargs={"order_uuid": order.uuid}))


@login_required
def bookings(request, status=None):
    print("bookings")
    current_page = "bookings"
    statuses = OrderStatus.objects.filter(is_active=True).exclude(id=1).values("name")
    user = request.user
    kwargs = dict()

    filtered_prices = request.GET.get('price')
    filtered_city = request.GET.get('city')
    filtered_guides = request.GET.getlist('guide')
    filtered_statuses = request.GET.getlist('status_input')

    place_id = request.GET.get("place_id")

    if filtered_prices:
        price = filtered_prices.split(";")
        if len(price)==2:

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
        orders = initial_orders.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
        bookings_nmb = orders.count()
        # print(kwargs)
        # print (orders)

    elif not user.is_anonymous():
        kwargs["status__name"] = status
        initial_orders = Order.objects.filter(tourist__user=user, status__name=status)#it is needed for citieas and guides list
        orders = initial_orders.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
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
    statuses = OrderStatus.objects.filter(is_active=True).exclude(id=1).values("name")

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
            orders = Order.objects.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
            # print("not status")
        else:
            kwargs["guide"] = guide
            kwargs["status__slug"] = status
            orders = Order.objects.filter(**kwargs).exclude(id__in=orders_to_exclude_ids).order_by('-id')#exclude pending status
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
    if current_role == "tourist" or not current_role:
        #check if a user is a tourist in an order
        try:
            tourist = user.touristprofile
            order = Order.objects.get(uuid=order_uuid, tourist=tourist)
            order.status_id = 3
            order.save(force_update=True)
            print("try 2")
            messages.success(request, _('Order has been successfully cancelled!'))
        except:
            messages.error(request, _('You have no permissions for this action!'))
    else:
        #check if a user is a guide
        try:
            guide = user.guideprofile
            order = Order.objects.get(uuid=order_uuid, guide=guide)
            order.status_id = 6
            order.save(force_update=True)
            print("try 1")
            print(order.status)
            messages.success(request, 'Order has been successfully cancelled!')
        except:
            messages.error(request, 'You have no permissions for this action!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def change_order_status(request, order_uuid, status_id):
    print("change order status")
    user = request.user

    current_role = request.session.get("current_role")
    print(current_role)
    if current_role == "tourist" or not current_role:
        #check if a user is a tourist in an order
        try:
            tourist = user.touristprofile
            order = Order.objects.get(uuid=order_uuid, tourist=tourist)

            # checking status transition consistancy for preventing hacking
            checking = checking_statuses(current_status_id=order.status.id, new_status_id=status_id)
            print("checking: %s" % checking)
            if checking == False:
                print("False")
                messages.error(request, 'You have no permissions for this action!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif status_id == "4":
                print("four")
                order.status_id = status_id
                order.save(force_update=True)
                messages.success(request, 'Order has been successfully marked as completed!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                print("else")
                order.status_id = status_id
                order.save(force_update=True)
                # messages.success(request, 'Order has been successfully cancelled!')
        except Exception as e:
            print(e)
            messages.error(request, 'You have no permissions for this action!')
    else:
        #check if a user is a guide
        try:
            print('TRY GUIDE')
            guide = user.guideprofile
            order = Order.objects.get(uuid=order_uuid, guide=guide)
            print('ORDER STATUS: ', order.status.id)
            print('NEW STATUS: ', status_id)

            # checking status transition consistancy for preventing hacking
            checking = checking_statuses(current_status_id=order.status.id, new_status_id=status_id)
            print('CHECKIG: ', checking)
            if checking == False:
                messages.error(request, 'You have no permissions for this action!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            print("3")
            print(status_id)
            order.status_id = status_id
            print("4")
            order.save(force_update=True)
            # messages.success(request, 'Order has been successfully cancelled!')
        except Exception as e:
            print(e)
            messages.error(request, 'You have no permissions for this action!')

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

                order.status_id = 4 #completed
                order.save(force_update=True)
                Review.objects.update_or_create(order=order, defaults=kwargs)
                messages.success(request, 'Review has been successfully created!')
                # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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

                #completing payment
                if order.status.id in [2, 4] and order.payment_status.id in [2, 3]:
                    # print("in")
                    payments = order.payment_set.all()
                    all_payment_successful = True
                    payments_errors = str()
                    for payment in payments.iterator():
                        transaction_id = payment.uuid
                        result = braintree.Transaction.submit_for_settlement(transaction_id)
                        if not result.is_success:
                            all_payment_successful = False
                            payments_errors += '%s ' % result.errors
                            # print(result.errors)
                        else:
                            order.status_id = 3 #partial payment reserved
                            payment.dt_paid = dt_now
                            payment.save(force_update=True)

                    if all_payment_successful:
                        order.status_id = 4 #completed
                        payment_status = PaymentStatus.objects.get(id=4)#fully paid
                        order.payment_status = payment_status
                        order.save(force_update=True)
                        Review.objects.update_or_create(order=order, defaults=kwargs)
                        messages.success(request, 'Review has been successfully created!')
                        order = Order.objects.get(uuid=order_uuid)
                    else:
                        messages.error(request, payments_errors)

        else:
            messages.error(request, 'You do not have permissions to access to this page!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    return render(request, 'orders/order_completing.html', locals())