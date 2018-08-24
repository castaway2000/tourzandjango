from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject
from chats.models import Chat
from django.db.models import Q


def site(request):
    site = SimpleLazyObject(lambda: get_current_site(request))
    protocol = 'https' if request.is_secure() else 'http'

    return {
        'site': site,
        'site_root': SimpleLazyObject(lambda: "{0}://{1}".format(protocol, site.domain)),
    }
