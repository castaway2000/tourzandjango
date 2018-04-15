from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from blog.models import BlogPost
from guides.models import GuideProfile
from locations.models import City, Location
from tourists.models import TouristProfile
from tours.models import Tour

class StaticSitemap(Sitemap):
    """Reverse 'static' views for XML sitemap."""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['about_us', 'tos', 'faq', 'contact_us', 'search_city', 'api_partner_application']

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
        return Tour.objects.all()

class GuideSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return GuideProfile.objects.all()