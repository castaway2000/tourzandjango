from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from mobile.models import GeoTracker, GeoTrip
from orders.models import Order, PaymentStatus
from users.models import GeneralProfile, User
from guides.models import GuideProfile
# from tourzan.settings import REDIS_ROOT

import redis as rs
from datetime import datetime
import json
r = rs.StrictRedis()
"""
HEADS UP, this section of the code requires spatialite or postgis for it to work.
"""

@api_view(['POST'])
def show_nearby_guides(request):
    """
    Token
    UserID
    Logged in users current location(latitude and longitude in float)
    Distance from their location to query (probably scaled from map view)
    :param request: 
    :return: 
    """
    try:
        user_id = int(request.POST['user_id'])
        lat = float(request.POST['latitude'])
        long = float(request.POST['longitude'])
        range = int(request.POST['range'])
        units = request.POST['units']
        point = Point(long, lat)

        GeoTracker.objects.get_or_create(user_id=user_id)
        GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, latitude=lat, longitude=long)
        field = no_geo_point_fields(GeoTracker)
        if units == 'km':
            guides = GeoTracker.objects.filter(geo_point__dwithin=(point, D(km=range)),
                                               user__guideprofile__isnull=False,
                                               is_online=True, trip_in_progress=False).values(*field)
        elif units == 'mi':
            guides = GeoTracker.objects.filter(geo_point__dwithin=(point, D(mi=range)),
                                               user__guideprofile__isnull=False,
                                               is_online=True, trip_in_progress=False).values(*field)
        else:
            return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': 'incorrect unit of distance'}]}))
        data = json.dumps(list(guides))
        return HttpResponse(data)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def get_trip_status(request):
    """
    params: 
    user_id
    
    returns:
    Guide user id
    Total Time limit in minutes(Signed integer number example 90 minutes)
    Remaining Time limit in minutes(Signed integer number example 90 minutes)
    Time limit automatic or manual flag
    Booking time.(MM-dd-yyyy HH:mm or specify yours)

    
    :param request: 
    :return: 
    """
    try:
        trip_id = int(request.POST['trip_id'])
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        user = GeoTracker.objects.get(user_id=trip_status.user_id)
        guide_profile = GeoTracker.objects.get(user_id=trip_status.guide_id)
        tdelta = trip_status.updated - trip_status.created
        if hasattr(guide_profile.user, 'guideprofile'):
            price = guide_profile.user.guideprofile.rate
            cost_update = round(float(tdelta.total_seconds() / 3600) * float(price), 2)
        else:
            return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': 'trip_status.guide_id has no guide profile'}]}))
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(), cost=cost_update)
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        data = {
            'guide_id': trip_status.guide_id,
            'total_time': trip_status.duration,
            'remianing_time': trip_status.time_remaining,
            'flag': trip_status.time_flag,
            'booking_created': trip_status.created.date().isoformat(),
            'guide_location': {'lat': guide_profile.latitude, 'lon': guide_profile.longitude},
            'user_location': {'lat': user.latitude, 'lon': user.longitude}
        }
        return HttpResponse(json.dumps(data))
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def extend_time(request):
    """
    Logged in Userid or Token
    Trip id
    Total extended time limit in minutes(Signed integer number example 90 minutes)
    Remaining Time limit in minutes(Signed integer number example 90 minutes)
    """
    try:
        req_id = int(request.POST['requester_id'])  # TODO: send notification to otehr user to accept of reject time.
        trip_id = int(request.POST['trip_id'])
        time_extending = int(request.POST['add_time'])
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        tdelta = trip_status.updated - trip_status.created
        tremaining = trip_status.time_remaining + time_extending
        guide_profile = GeneralProfile.objects.get(id=trip_status.guide_id).user
        if hasattr(guide_profile, 'guideprofile'):
            price = guide_profile.guideprofile.rate
            cost_update = round(float(tdelta.total_seconds() / 3600) * float(price), 2)
        else:
            return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': 'trip_status.guide_id has no guide profile'}]}))
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(),
                                                                    cost=cost_update, time_remaining=tremaining)

        data = json.dumps({'new_time': tremaining, 'cost': cost_update})
        return HttpResponse(data)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def book_guide(request):
    """
    :param request: 
    :return: 
    """
    try:
        token = request.POST['token']
        user_id = int(request.POST['user_id'])
        list_of_guides = json.loads(request.POST['guides'])
        lat = float(request.POST['latitude'])
        long = float(request.POST['longitude'])
        time_limit = int(request.POST['time_limit'])
        booking_type = request.POST['booking_type']
        booking_time = datetime.now()

        user = GeneralProfile.objects.get(user_id=user_id)
        point = Point(long, lat)
        user_interests = user.user.userinterest_set.values()
        user_language = user.get_languages()
        geotracker = GeoTracker.objects.filter(user__in=list_of_guides)\
            .filter(geo_point__dwithin=(point, D(km=50)))\
            .annotate(distance=Distance('geo_point', point))\
            .order_by('distance').values('user_id')
        general_profile = GeneralProfile.objects.filter(user_id__in=geotracker).values()
        data_set = {'guide': None, 'interest': [], 'interest_size': 0, 'language': None, 'language_size': 0}
        guides = []
        for g in general_profile:
            gdata = GeneralProfile.objects.get(user_id=g['user_id'])
            languages = [l for l in gdata.get_languages() if l in user_language]
            interests = [i for i in gdata.user.userinterest_set.values() if i in user_interests]
            data_set['guide'] = g['user_id']
            data_set['interest'] = interests
            data_set['interest_size'] = len(interests)
            data_set['language'] = languages
            data_set['language_size'] = len(languages)
            guides.append(data_set)
        languages = sorted(guides, key=lambda k: k['language_size'], reverse=True)
        aggregate = languages[0]
        print(aggregate)
        for l in languages:
            if l['interest_size'] > aggregate['interest_size'] and l['language_size'] > 0:
                aggregate = l
                break
        location = GeoTracker.objects.get(user_id=aggregate['guide'])
        guide = GeneralProfile.objects.get(user_id=aggregate['guide']).user.guideprofile

        data = json.dumps({'name': guide.name,
                           'picture': guide.profile_image.url,
                           'interests': aggregate['interest'],
                           'description': guide.overview,
                           'rate': float(guide.rate),
                           'rating': float(guide.rating),
                           'latitude': float(location.latitude),
                           'longitude': float(location.longitude)
                           })
        return HttpResponse(data)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def create_review(request):
    try:
        user_id = int(request.POST['user_id'])
        order_id = int(request.POST['order_id'])
        rating = float(request.POST['rating'])
        title = request.POST['title']
        feedback = request.POST['feedback']

        order = Order.objects.get(id=order_id)
        if order.guide_id == user_id:
            reviewed_user = order.tourist_id
            order.review.tourist_feedback_name = title
            order.review.tourist_feedback_text = feedback
            order.review.tourist_rating = rating
            order.review.is_guide_feedback = True
            if order.review.tourist_review_created:
                order.review.tourist_review_updated = datetime.now()
            else:
                order.review.tourist_review_created = datetime.now()
        else:
            reviewed_user = order.guide_id
            order.review.guide_feedback_name = title
            order.review.guide_feedback_text = feedback
            order.review.guide_rating = rating
            order.review.is_tourist_feedback = True
            if order.review.guide_review_created:
                order.review.guide_review_updated = datetime.now()
            else:
                order.review.guide_review_created = datetime.now()
        order.review.save()

        data = json.dumps({'detail': 'data is created'})
        return HttpResponse(data)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))



@api_view(['POST'])
def update_trip(request):
    print("update trip")
    try:
        print(1234)
        print(request.POST)
        status = request.POST['status']
        if status == 'login' or status == 'update':
            """
            user_id
            lat
            lon
            return channel
            """
            user_id = int(request.POST['user_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            point = Point(long, lat)
            GeoTracker.objects.get_or_create(user_id=user_id)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, latitude=lat, longitude=long)
            field = no_geo_point_fields(GeoTracker)
            user = GeoTracker.objects.filter(user_id=user_id).values(*field)
            return HttpResponse(json.dumps(list(user)))
        elif status == 'clockin':
            """
            guide_id
            return private channel and global channel
            """
            user_id = int(request.POST['user_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            point = Point(long, lat)
            GeoTracker.objects.get_or_create(user_id=user_id)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, is_online=True, latitude=lat, longitude=long)
            return HttpResponse(json.dumps({'status': 200, 'detail': 'user clocked in'}))
        elif status == 'clockout':
            """
            guide_id
            return private channel and global channel
            """
            user_id = int(request.POST['user_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            point = Point(long, lat)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, is_online=False, latitude=lat, longitude=long)
            return HttpResponse(json.dumps({'status': 200, 'detail': 'user clocked out'}))
        elif status == 'update_trip':
            trip_id = int(request.POST['trip_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            trip_status = GeoTrip.objects.get(id=trip_id, in_progress=True)
            trip_status.save(force_update=True)#AT: it saves nothing
            tdelta = trip_status.updated - trip_status.created
            guide_profile = GeneralProfile.objects.get(id=trip_status.guide_id).user
            if hasattr(guide_profile, 'guideprofile'):
                price = float(guide_profile.guideprofile.rate)
                cost_update = round(float(tdelta.total_seconds() / 3600) * price, 2)
                gtrip = GeoTrip.objects.filter(id=trip_id, in_progress=True)
                gtrip.update(duration=tdelta.total_seconds(), cost=cost_update)
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).values()
                print(trip_status)
                return HttpResponse(json.dumps({'latitude': lat, 'longitude': long, 'trip_status': list(trip_status)},
                                               default=datetime_handler))
        elif status == 'isAccepted':
            """
            if accepted subscribe to other users channel
            """
            #TODO: create order
            flag = request.POST['type']
            user_id = int(request.POST['user_id'])
            guide_id = int(request.POST['guide_id'])
            tdelta = 0
            if hasattr(request.POST, 'time') and flag == 'manual':
                tdelta = request.POST['time']
            kwargs = dict()
            guide = GeneralProfile.objects.get(id=guide_id).user.guideprofile.user_id
            tourist = GeneralProfile.objects.get(id=user_id).user.touristprofile.user_id

            kwargs['guide_id'] = guide_id
            kwargs['user_id'] = user_id
            kwargs['start'] = datetime.now()
            kwargs['number_persons'] = 2
            response = Order().create_order(**kwargs)
            order_id = response["order_id"]
            print (order_id)
            order = Order.objects.get(id=order_id)

            #setting agreed status to the order, skipping check for status flows inconsistancy.
            #In this case "pending" status will be changed to "agreed" status, which can not be true in existing order, because a tour should be approved
            #by guide as well
            order.change_status(user_id=user_id, current_role="guide", status_id=2, skip_status_flow_checking=True)

            GeoTracker.objects.filter(user_id=user_id).update(trip_in_progress=True)
            GeoTracker.objects.filter(user_id=guide_id).update(trip_in_progress=True)
            trip = GeoTrip.objects.update_or_create(user_id=user_id, guide_id=guide_id, in_progress=True,
                                                    duration=0, cost=0, time_flag=flag, time_remaining=tdelta,
                                                    order_id=order_id)
            return HttpResponse(json.dumps({'trip_id': trip[0].id, 'order_id': order_id}))
        elif status == 'isCancelled' or status == 'isDeclined':
            """
            token
            trip
            id
            """
            user_type = request.POST['type']
            user_id = int(request.POST['user_id'])
            trip_id = int(request.POST['trip_id'])
            current_role = "guide" #AT: put here dynamic role ("guide" or "tourist")
            if status == 'isCancelled':
                trip = GeoTrip.objects.get(id=trip_id)
                order = Order.objects.get(id=trip.order.id)
                response_data = order.change_status(user_id, current_role, status_id=6, skip_status_flow_checking=True) # Cancelled by guide
                print(response_data)
                if response_data["status"] == "success":
                    GeoTracker.objects.filter(user_id=trip.user_id).update(trip_in_progress=False)
            return HttpResponse(json.dumps({'status': status, 'user_id': user_id, 'user_type': user_type}))
        elif status == 'ended':
            """
            status
            token
            trip id
            total amount in USD
            """
            trip_id = request.POST['trip_id']
            trip_status = GeoTrip.objects.get(id=trip_id, in_progress=True)
            trip_status.save()  # this is to update the 'updated' timestamp
            tdelta = trip_status.updated - trip_status.created
            order = trip_status.order
            order.duration_seconds = tdelta.total_seconds()
            order.save(force_update=True)

            guide_id = trip_status.guide_id
            guide_profile = GuideProfile.objects.filter(id=guide_id).last()
            if guide_profile:
                price = float(guide_profile.rate)
                cost_update = round((tdelta.total_seconds() / 3600) * price, 2)
                GeoTrip.objects.filter(id=trip_id, in_progress=True)\
                    .update(duration=tdelta.total_seconds(), cost=cost_update)
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
                GeoTrip.objects.filter(id=trip_id, in_progress=True).update(in_progress=False)
                GeoTracker.objects.filter(user_id__in=[trip_status.guide_id, trip_status.user_id])\
                    .update(trip_in_progress=False)
                order.make_payment(guide_profile.user.id)
            else:
                return HttpResponse(json.dumps({'errors': [{'status': 400, 'error': 'guide_id has no guide profile'}]}))
            return HttpResponse(json.dumps({'trip_id': trip_status.id, 'price': trip_status.cost, 'isEnded': True}))
        return HttpResponse(json.dumps({'errors': [{'status': 412, 'detail': 'incorrect status value'}]}))
    except Exception as err:
        print(err)
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


def no_geo_point_fields(model):
    return [f.name for f in model._meta.get_fields() if f.name != 'geo_point']


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
