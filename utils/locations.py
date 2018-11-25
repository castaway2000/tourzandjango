from locations.models import City, Country


def get_city_country(place_id=None, city_slug=None):
    city = None
    country = None
    if place_id:
        try:
            city = City.objects.get(place_id=place_id)
        except:
            try:
                country = Country.objects.get(place_id=place_id)
            except:
                pass
    elif city_slug:
        city_slug = city_slug.lower()
        try:
            city = City.objects.get(slug=city_slug)
        except:
            pass
    return (city, country)