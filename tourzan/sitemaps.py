from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from blog.models import BlogPost
from guides.models import GuideProfile
from locations.models import City, Country, Location
from tourists.models import TouristProfile
from tours.models import Tour
import itertools


class StaticSitemap(Sitemap):
    """Reverse 'static' views for XML sitemap."""
    priority = 1.0
    changefreq = 'yearly'

    def items(self):
        return ['about_us', 'tos', 'faq', 'contact_us', 'search_city', 'api_partner_application', 'machu_picchu',
                'local_tour_guides', 'world_travel_guide', 'private_tour_guide', 'private_guide', 'travel_tour_guide',
                'tour_guide', 'tours_by_locals', 'affordable_tours', 'toursbylocals', 'tour_companies',
                'guided_travel_tours']

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.all()


class TourSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Tour.objects.filter(is_active=True)

class GuideSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return GuideProfile.objects.filter(is_active=True)


class CitySitemap(Sitemap):
    FIELDS = ("get_absolute_url", "get_city_tourism_url", "get_visit_city_url",
              "get_city_travel_guide_url", "get_city_guided_tours_url", "get_guided_tours_of_city_url",
              "get_private_tours_of_city_url", "get_city_travel_guide_url", "get_city_tours_url")
    changefreq = "daily"
    priority = 0.9

    def items(self):
        # This will return you all possible ("method_name", object) tuples instead of the
        # objects from the query set. The documentation says that this should be a list
        # rather than an iterator, hence the list() wrapper.
        return list(itertools.product(CitySitemap.FIELDS,
                                      City.objects.all()))

    def location(self, item):
        # Call method_name on the object and return its output
        return getattr(item[1], item[0])()


class CountrySitemap(Sitemap):
    FIELDS = ("get_absolute_url", "get_country_tourism_url", "get_visit_country_url",
              "get_country_travel_guide_url", "get_country_guided_tours_url", "get_guided_tours_of_country_url",
              "get_private_tours_of_country_url", "get_country_travel_guide_url", "get_country_tours_url")
    changefreq = "daily"
    priority = 0.9

    def items(self):
        # This will return you all possible ("method_name", object) tuples instead of the
        # objects from the query set. The documentation says that this should be a list
        # rather than an iterator, hence the list() wrapper.
        return list(itertools.product(CountrySitemap.FIELDS,
                                      Country.objects.all()))

    def location(self, item):
        # Call method_name on the object and return its output
        return getattr(item[1], item[0])()
