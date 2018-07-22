from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from mobile.models import GeoTracker, GeoTrip
from users.models import GeneralProfile, GuideProfile, UserInterest, User
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
        tdelta = trip_status.updated - trip_status.created
        guide_profile = GeneralProfile.objects.filter(id=trip_status.guide_id).get().user
        if hasattr(guide_profile, 'guideprofile'):
            price = guide_profile.guideprofile.rate
            cost_update = round(float(tdelta.total_seconds() / 3600) * float(price), 2)
        else:
            return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': 'trip_status.guide_id has no guide profile'}]}))
        GeoTrip.objects.filter(id=trip_id, in_progress=True).update(duration=tdelta.total_seconds(), cost=cost_update)
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        print('owo')
        data = {'guide_id': trip_status.guide_id, 'total_time': trip_status.duration,
                'remianing_time': trip_status.time_remaining, 'flag': trip_status.time_flag,
                'booking_created': trip_status.created.date().isoformat()}
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
        trip_id = int(request.POST['trip_id'])
        time_extending = int(request.POST['add_time'])
        trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
        tdelta = trip_status.updated - trip_status.created
        tremaining = trip_status.time_remaining + time_extending
        guide_profile = GeneralProfile.objects.filter(id=trip_status.guide_id).get().user
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
        list_of_guides = request.POST['guides']
        lat = float(request.POST['latitude'])
        long = float(request.POST['longitude'])
        time_limit = int(request.POST['time_limit'])
        booking_type = request.POST['booking_type']
        booking_time = datetime.now()

        user = GeneralProfile.objects.get(user_id=user_id)
        point = Point(long, lat)
        user_interests = user.user.userinterest_set.values()
        user_language = user.get_languages()
        geotracker = GeoTracker.objects.filter(user__in=list_of_guides).distance(point).order_by('distance')
        general_profile = GeneralProfile.objects.filter(user_id__in=geotracker.user).values()
        data_set = {'guide': None, 'interest': [], 'interest_size': 0, 'language': None, 'language_size': 0}
        guides = []
        for g in general_profile:
            languages = [l for l in g.get_languages() if l in user_language]
            interests = [i for i in g.user.userinterest_set.values() if i in user_interests]
            data_set['guide'] = g.user_id
            data_set['interest'] = interests
            data_set['interest_size'] = len(interests)
            data_set['language'] = languages
            data_set['language_size'] = len(languages)
            guides.append(data_set)
        languages = sorted(guides, key=lambda k: k['language_size'], reverse=True)
        aggregate = languages[0]
        for l in languages:
            if l['interest_size'] > aggregate['interest_size'] and l['language_size'] > 0:
                aggregate = l
                break
        guide = GuideProfile.objects.get(user_id=aggregate['user_id'])
        location = GeoTracker.objects.get(user_id=aggregate['user_id'])
        data = json.dumps({'name': guide.name,
                           'picture': guide.profile_image,
                           'interests': aggregate['interests'],
                           'description': guide.overview,
                           'rate': guide.rate,
                           'rating': guide.rating,
                           'latitude': location.latitude,
                           'longitude': location.longitude
                           })
        return HttpResponse(data)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def update_trip(request):
    try:
        status = request.POST['status']
        print(status)
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
            GeoTracker.objects.update_or_create(user_id=user_id, latitude=lat, longitude=long)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point)
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
            GeoTracker.objects.get(user_id=user_id)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, is_online=False, latitude=lat, longitude=long)
            return HttpResponse(json.dumps({'status': 200, 'detail': 'user clocked out'}))
        elif status == 'update_trip':
            trip_id = int(request.POST['trip_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            trip_status = GeoTrip.objects.get(id=trip_id, in_progress=True)
            trip_status.save(force_update=True)
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
            flag = request.POST['type']
            user_id = int(request.POST['user_id'])
            guide_id = int(request.POST['guide_id'])
            tdelta = 0
            if hasattr(request.POST, 'time') and flag == 'manual':
                tdelta = request.POST['time']
            GeoTracker.objects.filter(user_id=user_id).update(trip_in_progress=True)
            GeoTracker.objects.filter(user_id=guide_id).update(trip_in_progress=True)
            trip = GeoTrip.objects.update_or_create(user_id=user_id, guide_id=guide_id, in_progress=True,
                                                    duration=0, cost=0, time_flag=flag, time_remaining=tdelta)
            return HttpResponse(json.dumps({'trip_id': trip[0].id}))
            #TODO: create trip orders
        elif status == 'isCancelled' or status == 'isDeclined':
            """
            token
            trip
            id
            """
            user_type = request.POST['type']
            user_id = request.POST['user_id']
            trip_id = request.POST['trip_id']
            GeoTracker.objects.filter(user_id=user_id).update(trip_in_progress=False)
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
            guide_profile = GeneralProfile.objects.get(id=trip_status.guide_id).user
            if hasattr(guide_profile, 'guideprofile'):
                price = float(guide_profile.guideprofile.rate)
                cost_update = round((tdelta.total_seconds() / 3600) * price, 2)
                GeoTrip.objects.filter(id=trip_id, in_progress=True)\
                    .update(duration=tdelta.total_seconds(), cost=cost_update)
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
                GeoTrip.objects.filter(id=trip_id, in_progress=True).update(in_progress=False)
                # TODO: make the trip register in the database and process payments from phone.
            else:
                return HttpResponse(json.dumps({'errors': [{'status': 400, 'error': 'guide_id has no guide profile'}]}))
            return HttpResponse(json.dumps({'trip_id': trip_status.id, 'price': trip_status.cost, 'isEnded': True}))
        return HttpResponse(json.dumps({'errors': [{'status': 412, 'detail': 'incorrect status value'}]}))
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


def no_geo_point_fields(model):
    return [f.name for f in model._meta.get_fields() if f.name != 'geo_point']


def set_user_location(channel, user_type, user_id, lat, long):
    msg = str({'type': user_type, 'user_id': user_id, 'lat': lat, 'long':long})
    r.publish(channel=channel, message=msg)


def get_private_channel(user_type, user_id):
    channel = "{}{}".format(user_type, user_id)
    r.pubsub().subscribe(channel=channel)


def post_private_channel(user_type, user_id, lat, long, trip_time):
    channel = "{}{}".format(user_type, user_id)
    msg = str({'type': user_type, 'user_id': user_id, 'lat': lat, 'long': long})
    r.pubsub().publish(channel=channel, message=msg)


def get_global_channel():
    r.pubsub().subscribe(channel='global')


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
