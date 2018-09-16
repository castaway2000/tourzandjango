from django.utils.translation import activate
import datetime
from django.core.cache import cache
from tourzan.settings import USER_LASTSEEN_TIMEOUT
import time


# class ForceDefaultLanguageMiddleware(object):
#     """
#     Ignore Accept-Language HTTP headers
#
#     This will force the I18N machinery to always choose settings.LANGUAGE_CODE
#     as the default initial language, unless another one is set via sessions or cookies
#
#     Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
#     namely django.middleware.locale.LocaleMiddleware
#     """
#     def process_request(self, request):
#         activate('en')
#         pass


class TrackingActiveUserMiddleware:
    print("TrackingActiveUserMiddleware")
    """
    Middleware to set last processed request time ("last seen time") for a user.id to a cache table.
    It is used to decide if a user is online now or not
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_user = request.user
        if request.user.is_authenticated():
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.id), now, USER_LASTSEEN_TIMEOUT)
        return self.get_response(request)


class ReferralCodesGettingMiddleware:
    """
    Middleware is used for getting a referral code from the url and assigning it to the request session variable
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        data = request.GET
        if "ref" in data:
            referral_code = data.get("ref")
            request.session["referral_code"] = referral_code
        return self.get_response(request)