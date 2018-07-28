from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import City, Country


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


def all_countries(request):
    current_page = "all_countries"
    countries = Country.objects.filter(is_active=True)
    return render(request, 'locations/all_countries.html', locals())


def location_guides(request, country_slug, city_slug=None):
    print(country_slug)
    print(city_slug)
    kwargs = dict()
    if city_slug:
        kwargs["slug"] = city_slug
        kwargs["country__slug"] = country_slug
        obj = get_object_or_404(City, **kwargs)
    else:
        kwargs["slug"] = country_slug
        print(kwargs)
        obj = get_object_or_404(Country, **kwargs)
    return render(request, 'locations/location_guides.html', locals())