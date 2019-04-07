from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from orders.models import Order
from chats.models import Chat, ChatMessage
from locations.models import City
from coupons.models import Coupon, CouponUser
from django.utils.translation import ugettext as _
from django.db.models import Sum
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

@login_required()
def payment_methods(request):
    page = "payment_methods"
    user = request.user
    payment_methods = user.paymentmethod_set.filter(is_active=True)
    payment_customer, created = PaymentCustomer.objects.get_or_create(user=user)
    return render(request, 'payments/payment_methods.html', locals())


@login_required()
def payment_methods_adding(request):
    user = request.user

    #for using at template js for initializing of braintree form
    request.session['braintree_client_token'] = braintree.ClientToken.generate()
    payment_customer, created = PaymentCustomer.objects.get_or_create(user=user)

    if request.POST:
        payment_method_nonce = request.POST.get('payment_method_nonce')
        if payment_method_nonce:
            make_default = True if request.POST.get('is_default') else False
            response_data = payment_customer.payment_method_create(payment_method_nonce, make_default)

            #AT 31082018: transfer such code snippet to utils function later
            status = response_data["status"]
            message = response_data["message"]
            if status == "success":
                # messages.success(request, message)
                #redirecting after payment method adding if there is a pending order id
                #AT 02092018: this is needs to be tested with cases when user starts booking in the app and continues to do it
                # on the website.
                pending_order_uuid = request.session.get("pending_order")
                if pending_order_uuid:
                    del request.session["pending_order"]
                    messages.success(request, _('A new payment method was successfully added and now you can proceed with your order'))
                    return HttpResponseRedirect(reverse("order_payment_checkout", kwargs={"order_uuid": pending_order_uuid}))
                else:
                    messages.success(request, _('A new payment method was successfully added!'))
                    return HttpResponseRedirect(reverse("payment_methods"))
            else:
                messages.error(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'payments/payment_methods_adding.html', locals())


@login_required()
def payments(request):
    page = "payments"
    user = request.user
    payments = Payment.objects.filter(order__tourist__user=user).order_by("-id")
    payments_aggr = payments.aggregate(amount=Sum("amount"))
    payments_total_amount = payments_aggr.get("amount") if payments_aggr.get("amount") else 0
    return render(request, 'payments/payments.html', locals())


@login_required()
def payment_method_set_default(request, payment_method_id):
    user = request.user
    if payment_method_id:
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=user, is_active=True)
        response_data = payment_method.set_as_default()
        status = response_data["status"]
        message = response_data["message"]
        if status == "success":
            messages.success(request, message)
        else:
            messages.error(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def deleting_payment_method(request, payment_method_id):
    user = request.user
    if payment_method_id:
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=user, is_active=True)
        response_data = payment_method.deactivate()
        status = response_data["status"]
        message = response_data["message"]
        if status == "success":
            messages.success(request, message)
        else:
            messages.error(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def order_payment_checkout(request, order_uuid):
    user = request.user
    order = get_object_or_404(Order, uuid=order_uuid, tourist__user=user) #fix for preventing accessing to other tourist orders
    services_in_order = order.serviceinorder_set.all()
    city = order.guide.city_id
    country = City.objects.filter(id=city).values()[0]['full_location'].split(',')[-1].strip()
    illegal_country = False
    for i in ILLEGAL_COUNTRIES:
        if i == country:
            illegal_country = True
            break

    #adding variable to session for redirecting after adding a payment method
    user_payment_method = PaymentMethod.objects.filter(user=user, is_active=True).exists()
    if not user_payment_method:
        request.session["pending_order"] = order.uuid

    #check for preventing unauthorized access
    if order.tourist.user != user and order.guide.user != user:
        return HttpResponseRedirect(reverse("home"))

    if request.POST:
        data = request.POST
        guide = order.guide
        topic = "Chat with %s about order %s" % (guide.user.generalprofile.get_name(), order.uuid)
        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user,
                                                   order=order,
                                                   defaults={"topic": topic})

        message = data.get("message")
        if message:
            chat_message = ChatMessage.objects.create(chat=chat, message=message, user=user)
        if not illegal_country:
            tourist_email = order.tourist.user.email
            if order.tour and order.tour.type == "1":  # scheduled tour -> pay full amount from the beginning
                payment_processed = order.make_payment(user.id, True)
            else:
                payment_processed = order.reserve_payment(user.id)  # method on order model
            message = payment_processed["message"]
            if payment_processed["status"] == "error":
                messages.error(request, message)
            else:
                messages.success(request, message)
        else:
            order.making_mutual_agreement()  #method on order model
            messages.success(request, 'The guide has been successfully reserved!')

        #refresh a page to show "reserved payment" stamp
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'payments/order_payment_checkout.html', locals())
