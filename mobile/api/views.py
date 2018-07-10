from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from mobile.models import GeoTracker, GeoTrip
from users.models import GeneralProfile
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

        GeoTracker.objects.update_or_create(user_id=user_id, latitude=lat, longitude=long)
        GeoTracker.objects.filter(user_id=user_id).update(geo_point=point)
        if units == 'km':
            guides = GeoTracker.objects.filter(geo_point__dwithin=(point, D(km=range)),
                                               user__guideprofile__isnull=False,
                                               is_online=True, trip_in_progress=False).values()
        elif units == 'mi':
            guides = GeoTracker.objects.filter(geo_point__dwithin=(point, D(mi=range)),
                                               user__guideprofile__isnull=False,
                                               is_online=True, trip_in_progress=False).values()
        else:
            return HttpResponse(400)
        data = json.dumps({'nearby_guides': guides})
        return HttpResponse(data)
    except Exception as err:
        print(err)
        return HttpResponse(400)


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
        tdelta = trip_status.updated - trip_status.created
        guide_profile = GeneralProfile.objects.filter(id=trip_status.guide_id).get().user
        if hasattr('guideprofile', guide_profile):
            price = guide_profile.guideprofile.rate
            cost_update = tdelta.total_seconds() / 3600 * price
        else:
            return HttpResponse(400)
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(), cost=cost_update)
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        data = json.dumps({'guide_id': trip_status.guide_id, 'total_time': trip_status.duration,
                           'remianing_time': trip_status.time_remaining, 'flag': trip_status.time_flag,
                           'booking_created': trip_status.created.date()})
        return HttpResponse(data)
    except Exception as err:
        print(err)
        return HttpResponse(400)

@api_view(['POST'])
def extend_time(request):
    """
    Logged in Userid or Token
    Trip id
    Total extended time limit in minutes(Signed integer number example 90 minutes)
    Remaining Time limit in minutes(Signed integer number example 90 minutes)
    """
    try:
        trip_id = int(request.POST['trip_id'])
        time_extending = request.POST['add_time']
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        tdelta = trip_status.updated - trip_status.created
        tremaining = trip_status.time_remaining + time_extending
        guide_profile = GeneralProfile.objects.filter(id=trip_status.guide_id).get().user
        if hasattr('guideprofile', guide_profile):
            price = guide_profile.guideprofile.rate
            cost_update = tdelta.total_seconds() / 3600 * price
        else:
            return HttpResponse(400)
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(),
                                                                    cost=cost_update, time_remaining=tremaining)

        data = json.dumps({'new_time': tremaining, 'cost': cost_update})
        return HttpResponse(data)
    except Exception as err:
        print(err)
        return HttpResponse(400)

@api_view(['POST'])
def book_guide(request):
    """
    Logged in Userid
    Verify the Token
    Logged in users current location (latitude and longitude in float)
    Logged in users current address text
    Guide user id
    Time limit in minutes(Signed integer number example 90 minutes)
    Time limit automatic or manual flag
    Booking time.(MM-dd-yyyy HH:mm or specify yours)

    :param request: 
    :return: 
    """
    try:
        token = request.POST['token']
        user_id = int(request.POST['user_id'])
        guide_id = int(request.POST['guide_id'])
        lat = float(request.POST['latitude'])
        long = float(request.POST['longitude'])
        time_limit = int(request.POST['time_limit'])
        booking_type = request.POST['booking_type']
        booking_time = datetime.now()
        return HttpResponse(200)
    except Exception as err:
        print(err)
        return HttpResponse(400)


@api_view(['POST'])
def update_trip(request):
    try:
        status = request.POST['status']
        if status == 'login' or status == 'update':
            """
            user_id
            lat
            lon
            return channel
            """
            try:
                # user_type = request.POST['type']
                # guide_id = request.POST['guide_id']
                user_id = int(request.POST['user_id'])
                lat = float(request.POST['latitude'])
                long = float(request.POST['longitude'])
                point = Point(long, lat)
                GeoTracker.objects.update_or_create(user_id=user_id, latitude=lat, longitude=long)
                GeoTracker.objects.filter(user_id=user_id).update(geo_point=point)
                user = GeoTracker.objects.filter(user_id=user_id).values()
                data = json.dumps({'data': user})
                return HttpResponse(data)
                # channel = "{}{}".format(user_type, user_id)
                # r.pubsub().subscribe(channel, 'global')
            except Exception as err:
                print(err)
                return HttpResponse(400)

        elif status == 'clockin' or status == 'update_trip':
            """
            guide_id
            return private channel and global channel
            """
            user_id = int(request.POST['user_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            trip_id = request.POST['trip_id']
            point = Point(long, lat)
            if status == 'clockin':
                GeoTracker.objects.update_or_create(user_id=user_id, is_online=True, latitude=lat, longitude=long)
                GeoTracker.objects.filter(user_id=user_id).update(geo_point=point)

            # set_user_location('global', user_type, user_id, lat, long)
            if status == 'update':
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
                tdelta = trip_status.updated - trip_status.created
                guide_profile = GeneralProfile.objects.filter(id=trip_status.guide_id).get().user
                if hasattr('guideprofile', guide_profile):
                    price = guide_profile.guideprofile.rate
                    cost_update = tdelta.total_seconds()/3600 * price
                else:
                    return HttpResponse(400)
                GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(),
                                                                            cost=cost_update, latitude=lat,
                                                                            longitude=long, geo_point=point)
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
                data = json.dumps({'location': point, 'trip_status': trip_status})
                return HttpResponse(data)
            return HttpResponse(200)

        elif status == 'isAccepted':
            """
            if accepted subscribe to other users channel
            """
            # user_type = request.POST['type']
            user_id = request.POST['user_id']
            guide_id = request.POST['guide_id']
            GeoTracker.objects.filter(user_id=user_id).update(trip_in_progress=True)
            trip = GeoTrip.objects.update_or_create(user=user_id, guide=guide_id, in_progress=True)
            data = json.dumps({'trip_id': trip.id})
            HttpResponse(data)
            #TODO: create trip orders
            # get_private_channel(user_type, user_id)  # subscribe to opponents channel
            # r.pubsub().unsubscribe('global')
            # post_private_channel('traveler', user_id)
            # post_private_channel('guide', guide_id)

        elif status == 'isCancelled' or status == 'isDeclined':
            """
            token
            trip
            id
            """
            user_type = request.POST['type']
            user_id = request.POST['user_id']
            if status == 'isCancelled':
                GeoTracker.objects.filter(user_id=user_id).update(trip_in_progress=False)
                # get_global_channel()
            data = json.dumps({'status': status, 'user_id': user_id, 'user_type': user_type})
            return HttpResponse(data)

        elif status == 'ended':
            """
            status
            token
            trip id
            total amount in USD
            """
            trip_id = request.POST['trip_id']
            guide_id = request.POST['guide_id']
            end_trip(trip_id, guide_id)
        else:
            return HttpResponse(400)
        return HttpResponse(200)
    except Exception as err:
        print(err)
        return HttpResponse(400)


def end_trip(trip_id, guide_id):
    try:
        #TODO: make the trip register in the database and process payments from phone.
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        tdelta = trip_status.updated - trip_status.created
        guide_profile = GeneralProfile.objects.filter(id=guide_id).get().user
        if hasattr('guideprofile', guide_profile):
            price = guide_profile.guideprofile.rate
            cost_update = tdelta.total_seconds() / 3600 * price
        else:
            return HttpResponse(400)
        GeoTrip.objects.filter(id=trip_id, in_progress=True)\
            .update(duration=tdelta.total_seconds(), cost=cost_update)
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(in_progress=False)
        data = json.dumps({'trip_id': trip_status.id, 'price': trip_status.cost, 'isEnded': True})
        return HttpResponse(data)
        # channel = "{}{}".format(user_type, user_id)
        # r.pubsub().unsubscribe(channel)
        # get_global_channel()
        # r.pubsub().listen()
    except Exception as err:
        print(err)
        return HttpResponse(400)

def set_user_location(channel, user_type, user_id, lat, long):
    msg = str({'type': user_type, 'user_id':user_id, 'lat':lat, 'long':long})
    r.publish(channel=channel, message=msg)


def get_private_channel(user_type, user_id):
    channel = "{}{}".format(user_type, user_id)
    r.pubsub().subscribe(channel=channel)


def post_private_channel(user_type, user_id, lat, long, trip_time):
    channel = "{}{}".format(user_type, user_id)
    msg = str({'type': user_type, 'user_id':user_id, 'lat':lat, 'long':long})
    r.pubsub().publish(channel=channel, message=msg)


def get_global_channel():
    r.pubsub().subscribe(channel='global')


