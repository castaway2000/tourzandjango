from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from orders.models import Order
from chats.models import Chat, ChatMessage


from tourzan.settings import BRAINTREE_MERCHANT_ID, BRAINTREE_PUBLIC_KEY, BRAINTREE_PRIVATE_KEY
import braintree
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


@login_required()
def making_order_payment(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id)
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
    return render(request, 'payments/payments.html', locals())


@login_required()
def order_payment_checkout(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id)

    #check for preventing unauthorized access
    if order.tourist.user != user and order.guide.user != user:
        return HttpResponseRedirect(reverse("home"))

    if request.POST:
        print(request.POST)
        data = request.POST

        guide = order.guide
        topic = "Chat with %s" % guide.user.username

        print(user)
        print(guide.user)

        chat, created = Chat.objects.get_or_create(tour_id__isnull=True, tourist=user, guide=guide.user, defaults={"topic": topic})

        message = data.get("message")
        if message:
            chat_message = ChatMessage.objects.create(chat=chat, message=message, user=user)


        payment_processed = order.making_order_payment()
        if payment_processed == False:
            messages.error(request, 'Failure during processing a payment. Check the balance of your card!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.success(request, 'The payment has been successfully reserved!')

    return render(request, 'payments/order_payment_checkout.html', locals())