from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.http import JsonResponse
from .models import City, Country
from django.core.urlresolvers import reverse
from django.contrib import messages


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
    countries = Country.objects.filter(is_active=True).order_by("name")
    return render(request, 'locations/all_countries.html', locals())


def location_guides(request, country_slug, city_slug=None):
    kwargs = dict()
    if city_slug:
        kwargs["slug"] = city_slug
        kwargs["country__slug"] = country_slug
        obj = get_object_or_404(City, **kwargs)
    else:
        kwargs["slug"] = country_slug
        obj = get_object_or_404(Country, **kwargs)
    return render(request, 'locations/location_guides.html', locals())


def location_search_router(request):
    data = request.GET
    place_id = data.get("place_id")
    if place_id:
        city = City.objects.filter(place_id=place_id).last()
        if city:
            return HttpResponseRedirect(reverse("city_guides", kwargs={"country_slug":city.country.slug, "city_slug": city.slug}))
        else:
            country = Country.objects.filter(place_id=place_id).last()
            if country:
                return HttpResponseRedirect(reverse("country_guides", kwargs={"country_slug":city.country.slug }))

    messages.error(request, 'We do not have any tours or guides in your searching location yet! Check all the available locations at this page')
    return HttpResponseRedirect(reverse("all_countries"))