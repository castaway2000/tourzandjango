from django.shortcuts import render
from django.http import JsonResponse
from .models import City


# Create your views here.
def search_city(request):
    response_data = dict()
    results = list()

    if request.GET:

        data = request.GET
        city_name = data.get(u"q")
        print ("city name: %s" % city_name)
        cities = City.objects.filter(name__icontains=city_name)

        for city in cities:
            results.append({
                "id": city.original_name,
                "text": city.original_name
            })

    response_data = {
        "items": results,
        "more": "false"
    }
    return JsonResponse(response_data, safe=False)