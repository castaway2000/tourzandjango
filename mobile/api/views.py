from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.http.response import HttpResponse
# from tourzan.settings import REDIS_ROOT
import redis as rs
r = rs.Redis()


def create_trip(request):
    json = {}
    r.set('trip', json)
    return HttpResponse(200)


def get_trip(request):
    r.get('trip')
    return HttpResponse(200)


def update_trip(request):
    json = {}
    return HttpResponse(r.getset('trip', json))


def end_trip(request):
    r.delete('trip')
    return HttpResponse(200)


def set_guide_location(request):
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


def get_relative_distence(request):
    return True