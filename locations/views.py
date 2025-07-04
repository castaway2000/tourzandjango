from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.http import JsonResponse
from .models import City, Country, SearchLog
from .forms import NewLocationTourRequestForm
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from utils.google_recapcha import check_recaptcha
from utils.locations import get_city_country


# Create your views here.
def search_city(request):
    results = list()

    if request.GET:
        data = request.GET
        city_name = data.get(u"q")
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
    countries_count = countries.count()
    return render(request, 'locations/all_countries.html', locals())


def location_guides(request, country_slug=None, city_slug=None):
    kwargs = dict()
    if city_slug:
        kwargs["slug"] = city_slug
        kwargs["country__slug"] = country_slug
        obj = get_object_or_404(City, **kwargs)
        meta_title = obj.meta_title
        meta_descr = obj.meta_description
    else:
        kwargs["slug"] = country_slug
        obj = get_object_or_404(Country, **kwargs)
        meta_title = obj.meta_title
        meta_descr = obj.meta_description
    return render(request, 'locations/location_guides.html', locals())


def country_city_guides(request, country_slug):
    kwargs = dict()
    try:
        kwargs["slug"] = country_slug
        print(country_slug)
        obj = get_object_or_404(Country, **kwargs)
    except:
        kwargs["slug"] = str(country_slug).lower()
        country = City.objects.filter(slug=country_slug)[0].country.name
        kwargs["country__slug"] = str(country).lower()
        obj = get_object_or_404(City, **kwargs)
    return render(request, 'locations/location_guides.html', locals())


def machu_picchu(request):
    kwargs = dict()
    kwargs["slug"] = 'cusco'
    kwargs["country__slug"] = 'peru'
    obj = get_object_or_404(Country, **kwargs)
    return render(request, 'locations/location_guides.html', locals())


def location_search_router(request):
    try:
        data = request.GET
        place_id = data.get("place_id")
        search_term = data.get("search_term")
        if not search_term:
            search_term = data.get("location_search_input")
        city, country = get_city_country(place_id=place_id)
        SearchLog().create(request, city, country, search_term)
        if city:
            city = City.objects.filter(place_id=place_id).last()
            return HttpResponseRedirect(reverse("city_guides", kwargs={"country_slug": city.country.slug, "city_slug": city.slug}))
        elif country:
            country = Country.objects.filter(place_id=place_id).last()
            return HttpResponseRedirect(reverse("country_guides", kwargs={"country_slug": country.slug}))
        else:
            if place_id and place_id != "undefined":
                url = "%s?place_id=%s&search_term=%s" % (reverse("request_new_location_booking"), place_id, search_term)
            else:
                url = "%s?search_term=%s" % (reverse("request_new_location_booking"), search_term)
            return HttpResponseRedirect(url)
    except:
        messages.error(request,
                       'We do not have any tours or guides in your searching location yet! Check all the available locations at this page')
        return HttpResponseRedirect(reverse("all_countries"))


@check_recaptcha
def request_new_location_booking(request):
    user = request.user
    search_term = request.GET.get("search_term")
    place_id = request.GET.get("place_id")
    if search_term and len(search_term.split(",")) > 0:
        location_name = search_term.split(", ")[0]
    if place_id or search_term:
        form = NewLocationTourRequestForm(request.POST or None, user=user)
        if request.method == "POST":
            if form.is_valid() and request.recaptcha_is_valid:
                new_form = form.save(commit=False)
                new_form.location_name = search_term
                new_form.location_id = place_id
                if not user.is_anonymous():
                    new_form.user = user
                new_form.save()
                messages.success(request, _('Your request was successfully created! '
                                            'We will be in touch with you via email within 3 days'))
                hide_form = True
    return render(request, 'locations/request_new_location_booking.html', locals())
