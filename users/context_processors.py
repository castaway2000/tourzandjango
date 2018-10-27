from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject
from django.template import RequestContext
from django.shortcuts import render_to_response
from notifications.models import Banner


from tourzan.settings import ON_PRODUCTION
from chats.models import Chat
from django.db.models import Q

import tldextract


def site(request):
    site = SimpleLazyObject(lambda: get_current_site(request))
    protocol = 'https' if request.is_secure() else 'http'

    return {
        'site': site,
        'site_root': SimpleLazyObject(lambda: "{0}://{1}".format(protocol, site.domain)),
    }


def get_subdomain(request):
    url = request.META['HTTP_HOST']
    subdomain = tldextract.extract(url).subdomain
    return {'subdomain': subdomain}


def on_prod(request):
    print(on_prod)
    return {'on_prod': ON_PRODUCTION}


def if_banner(request):
    try:
        data = Banner.objects.get(active=True)
        title = data.title
        message = data.message
        url = data.url
        active = data.active
        context = {'title': title, 'message': message, 'url': url, 'is_active': active}
        return {'banner': context}
    except:
        return {'banner': False}