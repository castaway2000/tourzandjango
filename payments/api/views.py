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

from rest_framework.decorators import action
from .permissions import IsOwnerOnly
from django.shortcuts import get_object_or_404


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsOwnerOnly]
    http_method_names = ('get',)
    permissions_error_dict = {"status": "error", "message": "No such object or user has no permissions to get it!"}

    def get_queryset(self):
        user = self.request.user
        qs = PaymentMethod.objects.filter(user=user)
        return qs

    @action(methods=['get'], detail=False)
    def get_braintree_token(self, request):
        user = request.user
        braintree_client_token = braintree.ClientToken.generate()
        PaymentCustomer.objects.get_or_create(user=user)
        return Response({"braintree_client_token": braintree_client_token})

    @action(methods=['get'], detail=False)
    def create_payment_method(self, request):
        user = request.user
        data = request.GET
        payment_method_nonce = data.get("payment_method_nonce")
        make_default = True if data.get("is_default") else False
        payment_customer, created = PaymentCustomer.objects.get_or_create(user=user)
        response_data = payment_customer.payment_method_create(payment_method_nonce, make_default)
        return Response(response_data)

    #AT 02092018: permission_classes does not work here. But general View permissions are applied, when custom one for
    # the method were deleted.
    # Needs sending request to DRF github or its community for getting clarification.
    @action(methods=['get'], detail=True)
    def set_as_default_payment_method(self, request, pk=None):
        #AT 02092018: possible improve - use uuid instead of id. This needs researching.
        user = request.user
        payment_method = get_object_or_404(PaymentMethod, id=pk, user=user)
        if payment_method:
            response_data = payment_method.set_as_default()
            return Response(response_data)
        else:
            return Response(self.permissions_error_dict)

    @action(methods=['get'], detail=True)
    def deactivate_payment_method(self, request, pk=None):
        #AT 02092018: possible improve - use uuid instead of id. This needs researching.
        user = request.user
        payment_method = get_object_or_404(PaymentMethod, id=pk, user=user)
        if payment_method:
            response_data = payment_method.deactivate()
            return Response(response_data)
        else:
            return Response(self.permissions_error_dict)