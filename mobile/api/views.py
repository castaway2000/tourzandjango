from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from mobile.models import GeoTracker, GeoTrip
from orders.models import Order, PaymentStatus, Review
from users.models import GeneralProfile, User
from guides.models import GuideProfile
from pyfcm import FCMNotification
from tourzan.settings import FCM_API_KEY

import redis as rs
from datetime import datetime
import requests
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
        print(point)
        tracker = GeoTracker.objects.get_or_create(user_id=user_id)
        print(tracker)
        ref_tracker = GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, latitude=lat, longitude=long)
        print(ref_tracker)
        field = no_geo_point_fields(GeoTracker)
        print(field)
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
        print(guides)
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
            'order_id': trip_status.order.id,
            'guide_id': trip_status.guide_id,
            'tourist_id': trip_status.user_id,
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
        req_id = int(request.POST['requester_id'])  # TODO: send notification to other user to accept of reject time.
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
        user_id = int(request.POST['user_id'])
        list_of_guides = json.loads(request.POST['guides'])
        lat = float(request.POST['latitude'])
        long = float(request.POST['longitude'])
        time_limit = int(request.POST['time_limit'])
        booking_type = request.POST['booking_type']

        user = GeneralProfile.objects.get(user_id=user_id)
        point = Point(long, lat)
        user_interests = [i['interest_id'] for i in user.user.userinterest_set.values()]
        user_language = [l.language for l in user.get_languages() if l is not None]
        geotracker = GeoTracker.objects.filter(user__in=list_of_guides)\
            .filter(geo_point__dwithin=(point, D(km=50)))\
            .annotate(distance=Distance('geo_point', point))\
            .order_by('distance').values('user_id')
        general_profile = GeneralProfile.objects.filter(user_id__in=geotracker).values()
        guides = []
        for g in general_profile:
            data_set = {'guide': None, 'interest': [], 'interest_size': 0, 'language': [], 'language_size': 0}
            gdata = GeneralProfile.objects.get(user_id=g['user_id'])
            languages = [l.language for l in gdata.get_languages() if l is not None and l.language in user_language]
            interests = [i['interest_id'] for i in gdata.user.userinterest_set.values() if i['interest_id'] in user_interests]
            data_set['guide'] = g['user_id']
            data_set['interest'].extend(interests)
            data_set['interest_size'] = len(data_set['interest'])
            data_set['language'].extend(languages)
            data_set['language_size'] = len(data_set['language'])
            guides.append(data_set)
        sorted_by_languages = sorted(guides, key=lambda k: k['language_size'], reverse=True)
        print(sorted_by_languages)
        aggregate = sorted_by_languages[0]
        for l in sorted_by_languages:
            if aggregate['language_size'] == 0:
                if l['interest_size'] > aggregate['interest_size']:
                    aggregate = l
            else:
                if l['interest_size'] > aggregate['interest_size'] and l['language_size'] > 0:
                    aggregate = l
        print(aggregate)
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
        device_tokens = [guide.user.generalprofile.device_id]
        for device in device_tokens:
            payload = {
                "to": device,
                "notification": {
                    "title": "Tourzan",
                    "body": "You have received a booking offer!"
                },
                "data": {
                    "custom_notification": {
                        "body": "You have received a booking offer!",
                        "title": "Tourzan",
                        "color": "#00ACD4",
                        "priority": "high",
                        "icon": "ic_launcher",
                        "group": "GROUP",
                        "sound": "default",
                        "id": "id",
                        "show_in_foreground": True,
                        "extradata": {
                            'user_id': user.user_id,
                            'latitude': lat,
                            'longitude': long,
                            'time_limit': time_limit,
                            'type': 1,
                            'body': 'You have received a booking offer!'}
                    }
                }
            }
            push_notify(payload)
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
        review = Review.objects.get_or_create(order=order)[0]
        if order.guide_id == user_id:
            reviewed_user = order.tourist_id
            review.tourist_feedback_name = title
            review.tourist_feedback_text = feedback
            review.tourist_rating = rating
            review.is_guide_feedback = True
            if review.tourist_review_created:
                review.tourist_review_updated = datetime.now()
            else:
                review.tourist_review_created = datetime.now()
        else:
            reviewed_user = order.guide_id
            review.guide_feedback_name = title
            review.guide_feedback_text = feedback
            review.guide_rating = rating
            review.is_tourist_feedback = True
            if review.guide_review_created:
                review.guide_review_updated = datetime.now()
            else:
                review.guide_review_created = datetime.now()
        review.save()

        data = json.dumps({'detail': 'review created!'})
        return HttpResponse(data)
    except Exception as err:
        print(err)
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def update_trip(request):
    try:
        print(request.POST)
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
            device_id = str(request.POST['device_token'])
            point = Point(long, lat)
            GeoTracker.objects.get_or_create(user_id=user_id)
            devices = GeneralProfile.objects.filter(device_id=device_id)
            for d in devices:
                d.device_id=None
                d.save(force_update=True)
            GeneralProfile.objects.filter(user_id=user_id).update(device_id=device_id)
            GeoTracker.objects.filter(user_id=user_id).update(geo_point=point, latitude=lat, longitude=long)
            field = no_geo_point_fields(GeoTracker)
            user = GeoTracker.objects.filter(user_id=user_id).values(*field)
            trip = GeoTrip.objects.filter(user_id=user_id, in_progress=True)
            trip_guide = GeoTrip.objects.filter(guide_id=user_id, in_progress=True)
            # TODO: find guide_id from user id and check if it is still in progress.
            trip_id = None
            user_data = list(user)[0]
            if trip.exists():
                trip_id = trip[0].id
            elif trip_guide.exists():
                trip_id = trip_guide[0].id

            if trip_id:
                user_data['trip_in_progress'] = True
            user_data['trip_id'] = trip_id
            return HttpResponse(json.dumps(user_data))

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
            user = request.user
            trip_id = int(request.POST['trip_id'])
            lat = float(request.POST['latitude'])
            long = float(request.POST['longitude'])
            tracker = GeoTracker.objects.get(user=user)
            tracker.latitude = lat
            tracker.longitude = long
            tracker.geo_point = Point(lat, long)
            tracker.save(force_update=True)
            trip_status = GeoTrip.objects.get(id=trip_id, in_progress=True)
            trip_status.save(force_update=True) #AS: it refreshes the time last updated in the db
            tdelta = trip_status.updated - trip_status.created

            guide_profile = GeneralProfile.objects.get(user_id=trip_status.guide.id).user
            price = float(guide_profile.guideprofile.rate)
            cost_update = round(float(tdelta.total_seconds() / 3600) * price, 2)
            gtrip = GeoTrip.objects.filter(id=trip_id, in_progress=True)
            gtrip.update(duration=tdelta.total_seconds(), cost=cost_update)
            guide_tracker = GeoTracker.objects.get(user_id=gtrip[0].guide_id)
            tourist_tracker = GeoTracker.objects.get(user_id=gtrip[0].user_id)
            return HttpResponse(json.dumps({'tourist_latitude': tourist_tracker.latitude,
                                            'tourist_longitude': tourist_tracker.longitude,
                                            'guide_latitude': guide_tracker.latitude,
                                            'guide_longitude': guide_tracker.longitude,
                                            'trip_status': list(gtrip.values())}, default=datetime_handler))
        elif status == 'isAccepted':
            """
            if accepted subscribe to other users channel
            """
            print(True)
            flag = request.POST['type']
            user_id = int(request.POST['user_id'])
            guide_id = int(request.POST['guide_id'])
            tourist_check = GeoTrip.objects.filter(user_id=user_id, in_progress=True).count()
            guide_check = GeoTrip.objects.filter(guide_id=guide_id, in_progress=True).count()
            if not any([guide_check, tourist_check]):
                tdelta = 0
                if hasattr(request.POST, 'time') and flag == 'manual':
                    tdelta = request.POST['time']
                guide = GeneralProfile.objects.get(user_id=guide_id)
                tourist = GeneralProfile.objects.get(user_id=user_id)
                kwargs = dict()
                kwargs['guide_id'] = guide.user.guideprofile.id
                kwargs['user_id'] = tourist.user.touristprofile.user_id
                kwargs['start'] = datetime.now()
                kwargs['number_persons'] = 2
                print(kwargs)
                response = Order().create_order(**kwargs)
                order_id = response["order_id"]
                order = Order.objects.get(id=order_id)
                #setting agreed status to the order, skipping check for status flows inconsistancy.
                #In this case "pending" status will be changed to "agreed" status, which can not be true in existing order, because a tour should be approved
                #by guide as well
                order.change_status(user_id=user_id, current_role="guide", status_id=2, skip_status_flow_checking=True)
                trip = GeoTrip.objects.update_or_create(user_id=user_id, guide_id=guide_id, in_progress=True,
                                                        duration=0, cost=0, time_flag=flag, time_remaining=tdelta,
                                                        order_id=order_id)
                trackers = GeoTracker.objects.filter(user_id__in=[trip[0].user_id, trip[0].guide_id])
                for t in trackers:
                    t.trip_in_progress = True
                    t.save(force_update=True)

                device_tokens = [trip[0].user.generalprofile.device_id, trip[0].guide.generalprofile.device_id]
                for device in device_tokens:
                    payload = {
                        "to": device,
                        "notification": {
                            "title": "Tourzan",
                            "body": "The trip was accepted!"
                        },
                        "data": {
                            "custom_notification": {
                                "body": "The trip was accepted!",
                                "title": "Tourzan",
                                "color": "#00ACD4",
                                "priority": "high",
                                "icon": "ic_launcher",
                                "group": "GROUP",
                                "sound": "default",
                                "id": "id",
                                "show_in_foreground": True,
                                "extradata": {
                                    'trip_id': trip[0].id,
                                    'type': 2,
                                    'guide_generalprofile_id': trip[0].guide_id,
                                    'tourist_general_profile_id': trip[0].user_id,
                                    'body': 'Get ready for an adventure!'
                                }
                            }
                        }
                    }
                    push_notify(payload)
                return HttpResponse(json.dumps({'trip_id': trip[0].id, 'order_id': order_id}))
            else:
                return HttpResponse(json.dumps({'errors': [{'status': 412, 'detail': 'one of the users is already in a trip'}]}))

        elif status == 'isCancelled' or status == 'isDeclined':
            """
            token
            trip
            id
            """
            user_type = request.POST['type']
            user_id = int(request.POST['user_id'])
            trip_id = int(request.POST['trip_id'])
            if status == 'isCancelled':
                trip = GeoTrip.objects.get(id=trip_id)
                current_role = "guide"
                if trip.user_id == user_id:
                    current_role = 'tourist'
                order = Order.objects.get(id=trip.order.id)
                response_data = order.change_status(user_id, current_role, status_id=6, skip_status_flow_checking=True) # Cancelled by guide
                print(response_data)
                if response_data["status"] == "success":
                    GeoTracker.objects.filter(user_id__in=[trip.user_id, trip.guide_id]).update(trip_in_progress=False)
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
            guide_profile = GeneralProfile.objects.get(user_id=guide_id).user.guideprofile
            if guide_profile:
                price = float(guide_profile.rate)
                cost_update = round((tdelta.total_seconds() / 3600) * price, 2)
                GeoTrip.objects.filter(id=trip_id, in_progress=True)\
                    .update(duration=tdelta.total_seconds(), cost=cost_update)
                trip_status = GeoTrip.objects.filter(id=trip_id, in_progress=True).get()
                GeoTrip.objects.filter(id=trip_id, in_progress=True).update(in_progress=False)
                GeoTracker.objects.filter(user_id__in=[trip_status.guide_id, trip_status.user_id])\
                    .update(trip_in_progress=False)
                order.make_payment(guide_profile.user.id, True)
            else:
                return HttpResponse(json.dumps({'errors': [{'status': 400, 'error': 'guide_id has no guide profile'}]}))
            device_tokens = [trip_status.user.generalprofile.device_id, trip_status.guide.generalprofile.device_id]
            for device in device_tokens:
                payload = {
                    "to": device,
                    "notification": {
                        "title": "Tourzan",
                        "body": "Your trip on tourzan has completed successfully!"
                    },
                    "data": {
                        "custom_notification": {
                            "body": "Your trip on tourzan has completed successfully.",
                            "title": "Tourzan",
                            "color": "#00ACD4",
                            "priority": "high",
                            "icon": "ic_launcher",
                            "group": "GROUP",
                            "sound": "default",
                            "id": "id",
                            "show_in_foreground": True,
                            "extradata":
                                {'trip_id': trip_id,
                                 'order_id': order.id,
                                 'guide_generalprofile_id': trip_status.guide_id,
                                 'tourist_general_profile_id': trip_status.user_id,
                                 'type': 3,
                                 'body': 'Your trip on tourzan has completed successfully.'}
                        }
                    }
                }
                push_notify(payload)
            return HttpResponse(json.dumps({'trip_id': trip_status.id,
                                            'order_id': order.id,
                                            'price': round(order.total_price, 2),
                                            'tourist_id': trip_status.user_id,
                                            'guide_id': trip_status.guide_id,
                                            'tourist_trip_fees': round(order.fees_tourist, 2),
                                            'guide_trip_fees': round(order.fees_guide, 2),
                                            'guide_pay': round(order.guide_payment, 2),
                                            'isEnded': True}, cls=DjangoJSONEncoder))
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


def push_notify(payload):
    try:
        fcm = "https://fcm.googleapis.com/fcm/send"
        send = requests.post(fcm, headers={'Authorization': "key={}".format(FCM_API_KEY),
                                           'Content-Type': 'application/json; UTF-8'}, json=payload)
        print(send.text)
        print(send.status_code)
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))
