from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from mobile.models import GeoTracker
# from tourzan.settings import REDIS_ROOT

import redis as rs
from datetime import datetime
import json
r = rs.StrictRedis()


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
    user_id = request.POST['user_id']
    lat = request.POST['latitude']
    long = request.POST['longitude']
    point = Point(long, lat)
    GeoTracker.objects.update_or_create(user_id=user_id, latitude=lat, longitude=long, geo_point=point)
    guides = GeoTracker.objects.filter(geo_point__dwithin=(point, D(km=10)),
                                       user__guideprofile__isnull=False,
                                       is_online=True)
    data = json.dumps({'nearby_guides': guides})
    return HttpResponse(data)


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
    user_id = request.POST['user_id']
    guide_id = 12
    total_time = 123456789 # seconds
    time_limt_flag = 'Automatic'  # or manual flag
    booking_datetime = str(datetime.now())
    data = json.dumps({'guide_id': guide_id, 'total_time': total_time, 'timeflag': time_limt_flag,
                       'booked_date': booking_datetime})

    return HttpResponse(data)


@api_view(['POST'])
def extend_time(request):
    """
    Logged in Userid or Token
    Trip id
    Total extended time limit in minutes(Signed integer number example 90 minutes)
    Remaining Time limit in minutes(Signed integer number example 90 minutes)
    """
    token = request.POST['token']
    user_id = request.POST['user_id']
    trip_id = request.POST['trip_id']
    time_extending = request.POST['add_time']
    return HttpResponse(200)


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
    token = request.POST['token']
    user_id = request.POST['user_id']
    guide_id = request.POST['guide_id']
    lat = request.POST['latitude']
    long = request.POST['longitude']
    time_limit = request.POST['time_limit']
    booking_type = request.POST['booking_type']
    booking_time = datetime.now()

    return HttpResponse(200)


@api_view(['POST'])
def update_trip(request):
    status = request.POST['status']
    if status == 'login':
        """
        user_id
        lat
        lon
        return channel
        """
        user_type = request.POST['type']
        user_id = request.POST['user_id']
        channel = "{}{}".format(user_type, user_id)
        r.pubsub().subscribe(channel, 'global')

    elif status == 'clockin' or status == 'update':
        """
        guide_id
        return private channel and global channel
        """
        user_type = request.POST['type']
        user_id = request.POST['user_id']
        lat = request.POST['latitude']
        long = request.POST['longitude']
        point = Point(long, lat)
        GeoTracker.objects.update_or_create(user_id=user_id, is_online=True,
                                            latitude=lat, longitude=long, geo_point=point)
        set_user_location('global', user_type, user_id, lat, long)

    elif status == 'isAccepted':
        """
        if accepted subscribe to other users channel
        token
        trip
        user_id
        guide_id
        """
        user_type = request.POST['type']
        user_id = request.POST['user_id']
        guide_id = request.POST['guide_id']
        get_private_channel(user_type, user_id)  # subscribe to opponents channel
        r.pubsub().unsubscribe('global')
        post_private_channel('traveler', user_id)
        post_private_channel('guide', guide_id)

    elif status == 'isCancelled' or status == 'isDeclined':
        """
        token
        trip
        id
        """
        user_type = request.POST['type']
        user_id = request.POST['user_id']
        if status == 'isCancelled':
            get_global_channel()
        elif status == 'isDeclined':
            list_reasons = ['not enough money', 'forgot to clock out']

            data = json.dumps({'status': 'declined', 'reason': list_reasons, 'user_id': user_id,
                               'user_type': user_type})
            return HttpResponse(data)

    elif status == 'ended':
        """
        status
        token
        trip id
        total amount in USD
        """
        user_type = request.POST['type']
        user_id = request.POST['user_id']
        end_trip(user_type, user_id)
    else:
        return HttpResponse(400)
    return HttpResponse(200)


def end_trip(user_type, user_id):
        # token = request.POST['token']
        # trip_id = request.POST['trip_id']
        # ammount = request.POST['ammount']
        #TODO: make the trip register in the database and process payments from phone.
        channel = "{}{}".format(user_type, user_id)
        r.pubsub().unsubscribe(channel)
        get_global_channel()
        r.pubsub().listen()


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


