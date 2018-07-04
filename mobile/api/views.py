from rest_framework.decorators import detail_route, list_route, api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
# from tourzan.settings import REDIS_ROOT
import redis as rs
from datetime import datetime
import json
r = rs.Redis()


# @list_route()
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


# @list_route()
@api_view(['POST'])
def extend_time(requst):
    """
    Logged in Userid or Token
    Trip id
    Total extended time limit in minutes(Signed integer number example 90 minutes)
    Remaining Time limit in minutes(Signed integer number example 90 minutes)
    """
    return HttpResponse(200)


# @list_route()
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
    return HttpResponse(200)


# @list_route()
@api_view(['POST'])
def update_trip(request):
    token = request.POST['token']
    trip_id = request.POST['trip_id']
    status = request.POST['status']
    if status == 'create':
        """
        token
        user_id
        guide_id
        """
        json = {}
    elif status == 'isAccepted':
        """
        token
        trip
        id
        """
        json = {}
    elif status == 'isCancelled':
        """
        token
        trip
        id
        """
        json = {}
    elif status == 'ended':
        """
        status
        token
        trip id
        total amount in USD
        """
        json = {}

    else:
        return HttpResponse(400)
    return HttpResponse(200)


def end_trip(req):
        # token = request.POST['token']
        # trip_id = request.POST['trip_id']
        # ammount = request.POST['ammount']
        # r.delete('trip')
    json = {}


def set_guide_location(request):
    if request.POST:
        lat, long = request.POST['latitude'], request.POST['longitude']

    json_data = {}
    rtype = ['add', 'update', 'remove']
    lat = 27.123456
    lon = -89.098765
    guide_id = 21
    if rtype == 'add' or 'update':
        r.geoadd(json_data)
    elif rtype == 'remove':
        r.delete(json_data)


def set_customer_location(request):
    json_data = {}
    rtype = ['add', 'update', 'remove']
    lat = 27.123456
    lon = -89.098765
    guide_id = 21
    if rtype == 'add' or 'update':
        r.geoadd(json_data)
    elif rtype == 'remove':
        r.delete(json_data)