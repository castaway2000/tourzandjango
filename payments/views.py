from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from .models import *

from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRIVATE_KEY
import braintree
braintree.Configuration.configure(braintree.Environment.Sandbox,
    merchant_id=BRAINTREE_MERCHANT_ID,
    public_key=BRAINTREE_PUBLIC_KEY,
    private_key=BRAINTREE_PRIVATE_KEY
)



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


def payment_methods_adding(request):
    user = request.user
    request.session['braintree_client_token'] = braintree.ClientToken.generate()

    if request.POST:
        print(request.POST)

        payment_method_nonce = request.POST['payment_method_nonce']
        result = braintree.PaymentMethod.create({
            "customer_id": user.paymentcustomer.uuid,
            "payment_method_nonce": payment_method_nonce,
            "options": {
                "verify_card": True,
                # "fail_on_duplicate_payment_method": True,
                # "make_default": True #first payment method of a customer will be marked as "default"
            }
        })

        print(result)
        print(result.payment_method.token)

        response_data = result.payment_method
        token = response_data.token

        kwargs = {
            "user": user,
            "token": token
        }

        #improve for storing data for paypal
        # if "credit_card" in response_data:
        kwargs["is_default"] = response_data.default

        last_4_digits = response_data.verifications[0]["credit_card"]["last_4"]
        card_number = "XXXX-XXXX-XXXX-%s" % last_4_digits
        kwargs["card_number"] = card_number

        card_type = response_data.verifications[0]["credit_card"]["card_type"]
        card_type, created = CardType.objects.get_or_create(name=card_type)

        kwargs["card_type"] = card_type

        PaymentMethod.objects.create(**kwargs)

        return HttpResponseRedirect(reverse("payment_methods"))
    return render(request, 'payments/payment_methods_adding.html', locals())


def making_order_payment(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id)
    if order.tourist.user == user:
        payment_method = PaymentMethod.objects.filter(is_active=True).order_by('is_default', '-id').first()

        result = braintree.PaymentMethodNonce.create(payment_method.token)
        payment_method_nonce = result.payment_method_nonce.nonce

        result = braintree.Transaction.sale({
            "amount": order.total_price,
            "payment_method_nonce": payment_method_nonce,
            "options": {
                "submit_for_settlement": False
            }
        })

        print (result)

        if result.is_success:
            data = result.transaction

            payment_uuid = data.id
            amount = data.amount
            currency = data.currency_iso_code
            currency, created = Currency.objects.get_or_create(name=currency)

            Payment.objects.create(order=order, payment_method=payment_method,
                                   uuid=payment_uuid, amount=amount, currency=currency)

            order.status_id = 5 #paid
            order.save(force_update=True)

            messages.success(request, 'A Payment was successfully completed!')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            messages.error(request, 'Failure during processing a payment. Check the balance of your card!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return HttpResponseRedirect(reverse("bookings"))


def payments(request):
    page = "payments"
    user = request.user
    payments = Payment.objects.filter(order__tourist__user=user)
    return render(request, 'payments/payments.html', locals())
