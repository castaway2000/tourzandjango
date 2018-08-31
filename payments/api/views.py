from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from ..models import *
from .serializers import *

from django.db.models import Q
from django.shortcuts import get_object_or_404
from utils.api_helpers import FilterViewSet
from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY,  BRAINTREE_PRIVATE_KEY, ILLEGAL_COUNTRIES, ON_PRODUCTION
import braintree
if ON_PRODUCTION:
    braintree.Configuration.configure(braintree.Environment.Production,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )
else:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
        merchant_id=BRAINTREE_MERCHANT_ID,
        public_key=BRAINTREE_PUBLIC_KEY,
        private_key=BRAINTREE_PRIVATE_KEY
        )


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', "patch")

    def get_queryset(self):
        user = self.request.user
        qs = PaymentMethod.objects.filter(user=user)
        return qs

    @list_route()
    def get_braintree_token(self, request):
        user = request.user
        braintree_client_token = braintree.ClientToken.generate()
        PaymentCustomer.objects.get_or_create(user=user)
        return Response({"braintree_client_token": braintree_client_token})

    @list_route()
    def create_payment_method(self, request):
        user = request.user
        data = request.GET
        payment_method_nonce = data.get("payment_method_nonce")
        make_default = True if data.get("is_default") else False
        payment_customer, created = PaymentCustomer.objects.get_or_create(user=user)
        response_data = payment_customer.payment_method_create(payment_method_nonce, make_default)
        return Response(response_data)