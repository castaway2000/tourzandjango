import json, hmac, hashlib, time, requests
from requests.auth import AuthBase
from tourzan.settings import PAYMENT_RAILS_KEY, PAYMENT_RAILS_SECRET


class PaymentRailsWidget(object):
    widget_base_url = "https://widget.paymentrails.com"
    api_key = PAYMENT_RAILS_KEY
    secret_key = PAYMENT_RAILS_SECRET

    def get_widget_url(self):
        timestamp = str(int(time.time()))
        email = "test@gmail.com"
        guide_id = "123"
        query_string = "email=%s&refid=%s&ts=%s&key=%s" % (email, guide_id, timestamp, self.api_key)
        signiture = self.create_signiture(query_string)
        widget_link = "%s?%s&sign=%s" % (self.widget_base_url, query_string, signiture)

        return widget_link

    def create_signiture(self, query_string):
        secret_key = self.secret_key.encode('utf-8')
        query_string = query_string.encode('utf-8')
        hashed = hmac.new(secret_key, query_string, digestmod=hashlib.sha256)
        signature = hashed.hexdigest()
        return signature


class PaymentRailsAuth(AuthBase):
    api_key = PAYMENT_RAILS_KEY
    secret_key = PAYMENT_RAILS_SECRET

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = '\n'.join([timestamp, request.method, request.path_url, (request.body or ''), ''])
        message = message.encode('utf-8')
        secret_key = self.secret_key.encode('utf-8')
        hashed = hmac.new(secret_key, message, digestmod=hashlib.sha256)
        signature = hashed.hexdigest()
        request.headers.update({
            'Authorization': 'prsign %s:%s' % (self.api_key, signature),
            'X-PR-Timestamp': timestamp,
        })
        return request