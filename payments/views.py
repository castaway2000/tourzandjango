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
    if created:
        result = braintree.Customer.create({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
        payment_customer.uuid = result.customer.id
        payment_customer.save(force_update=True)

    return render(request, 'payments/payment_methods.html', locals())


@login_required()
def payment_methods_adding(request):
    user = request.user

    #for using at template js for initializing of braintree form
    request.session['braintree_client_token'] = braintree.ClientToken.generate()
    payment_customer, created = PaymentCustomer.objects.get_or_create(user=user)
    if created:
        result = braintree.Customer.create({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
        payment_customer.uuid = result.customer.id
        payment_customer.save(force_update=True)

    if request.POST:
        payment_method_nonce = request.POST.get('payment_method_nonce')
        if payment_method_nonce:
            result = braintree.PaymentMethod.create({
                "customer_id": payment_customer.uuid,
                "payment_method_nonce": payment_method_nonce,
                "options": {
                    "verify_card": True,
                    # "fail_on_duplicate_payment_method": True,
                    # True #first payment method of a customer will be marked as "default"

                    #just checkbox without being a part of a form returns "on" instead of True if it is checked
                    "make_default": True if request.POST.get('is_default') else False
                }
            })

            # print(result)
            # print(result.payment_method.token)
            # print(result.payment_method.__class__.__name__)

            try:
                response_data = result.payment_method
                token = response_data.token
                kwargs = {
                    "user": user,
                    "token": token
                }

                #depending on payment method different set of fields should be added
                if result.payment_method.__class__.__name__ == 'CreditCard':
                    kwargs["is_default"] = response_data.default
                    last_4_digits = response_data.verifications[0]["credit_card"]["last_4"]
                    card_number = "XXXX-XXXX-XXXX-%s" % last_4_digits
                    kwargs["card_number"] = card_number
                    card_type = response_data.verifications[0]["credit_card"]["card_type"]
                    card_type, created = PaymentMethodType.objects.get_or_create(name=card_type)
                    kwargs["type"] = card_type
                    PaymentMethod.objects.create(**kwargs)

                elif result.payment_method.__class__.__name__ == 'PayPalAccount':#paypal
                    print ("PayPal")
                    kwargs["is_default"] = response_data.default
                    kwargs["is_paypal"] = True
                    kwargs["paypal_email"] = response_data.email
                    type, created = PaymentMethodType.objects.get_or_create(name="paypal")
                    kwargs["type"] = type
                    PaymentMethod.objects.create(**kwargs)

                #redirecting after payment method adding if there is a pending order id
                pending_order_uuid = request.session.get("pending_order")
                if pending_order_uuid:
                    del request.session["pending_order"]
                    messages.success(request, _('A new payment method was successfully added and now you can proceed with your order'))
                    return HttpResponseRedirect(reverse("order_payment_checkout", kwargs={"order_uuid": pending_order_uuid}))
                else:
                    messages.success(request, _('A new payment method was successfully added!'))
                    return HttpResponseRedirect(reverse("payment_methods"))
            except:
                messages.success(request, _('A new payment method was successfully added!'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'payments/payment_methods_adding.html', locals())


@login_required()
def making_order_payment(request, order_uuid):
    user = request.user
    order = Order.objects.get(uuid=order_uuid)
    if order.tourist.user == user:
        payment_method = PaymentMethod.objects.filter(is_active=True).order_by('is_default', '-id').first()
        amount = "%s" % float(order.total_price)

        result = braintree.Transaction.sale({
            "amount": amount,
            "payment_method_token": payment_method.token,
            "options": {
                "submit_for_settlement": False
            }
        })

        if result.is_success:
            data = result.transaction

            payment_uuid = data.id
            amount = data.amount
            currency = data.currency_iso_code
            currency, created = Currency.objects.get_or_create(name=currency)

            Payment.objects.create(order=order, payment_method=payment_method,
                                   uuid=payment_uuid, amount=amount, currency=currency)

            order.status_id = 5 #payment reserved
            order.payment_status_id = 2 #payment reserved
            order.save(force_update=True)
            messages.success(request, 'A Payment was successfully completed!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            #order status is "pending" by default after an order was created
            messages.error(request, 'Failure during processing a payment. Check the balance of your card!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse("bookings"))


@login_required()
def payments(request):
    page = "payments"
    user = request.user
    payments = Payment.objects.filter(order__tourist__user=user).order_by("-id")
    payments_aggr = payments.aggregate(amount=Sum("amount"))
    payments_total_amount = payments_aggr.get("amount") if payments_aggr.get("amount") else 0
    return render(request, 'payments/payments.html', locals())


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
        topic = "Chat with %s" % guide.user.generalprofile.first_name
        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user,
                                                   order=order,
                                                   defaults={"topic": topic})

        message = data.get("message")
        if message:
            chat_message = ChatMessage.objects.create(chat=chat, message=message, user=user)
        if not illegal_country:
            payment_processed = order.reserve_payment(user.id)
            if not payment_processed:
                messages.error(request, 'Failure during processing a payment. Check the balance of your card!')
            else:
                messages.success(request, 'The payment has been successfully reserved!')
        else:
            order.making_mutual_agreement()
            messages.success(request, 'The guide has been successfully reserved!')

        #refresh a page to show "reserved payment" stamp
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'payments/order_payment_checkout.html', locals())


@login_required()
def deleting_payment_method(request, payment_method_id):
    user = request.user
    if payment_method_id:
        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id, user=user, is_active=True)
            result = braintree.PaymentMethod.delete(payment_method.token)
            if result.is_success:
                payment_method.is_active = False
                payment_method.save()
                messages.success(request, 'Payment method has been deleted successfully!')
            else:
                messages.error(request, 'Failure during deleting a payment method!')
        except Exception as e:
            messages.error(request, 'No such payment method was found!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def payment_method_set_default(request, payment_method_id):
    user = request.user
    if payment_method_id:
        try:
            payment_method = PaymentMethod.objects.get(id=payment_method_id, user=user, is_active=True)

            #all other Payment methods on Braintree side will be automatically updated to make_default = False
            result = braintree.PaymentMethod.update(payment_method.token, {
                "options":{
                    "make_default": True,
                    "verify_card": False,
                }
            })
            # print(result)
            if result.is_success:
                payment_method.is_default = True
                payment_method.save()
                messages.success(request, 'New default payment method has been applied successfully!')
            else:
                messages.error(request, 'Failure during changing a default payment method!')
        except Exception as e:
            messages.error(request, 'No such payment method was found!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

