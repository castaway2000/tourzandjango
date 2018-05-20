from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from coupons.models import Coupon, CouponUser
from orders.models import Order


@login_required()
def coupon_validation(request):
    data = request.POST
    order_id = data.get("order_id")
    coupon_code = data.get('coupon', None)
    user = request.user
    data = {'is_used': 'invalid'}
    if coupon_code and order_id:
        order = None
        try:
            order = Order.objects.get(id=order_id)
        except:
            pass
        if order and not order.coupon and order.status.id == 1:#coupons can be applied for orders only in pending status
            coupon = None
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    order.coupon = coupon
                    order.save(force_update=True)
                except:
                    pass
            if coupon:
                coupon_code = coupon_code.strip()
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.get_if_more_users_available():
                        coupon_user, created = CouponUser.objects.get_or_create(user_id=user.id, coupon=coupon)
                        redeemed = coupon_user.redeemed_at
                        discount = coupon_user.coupon.value
                        coupon_type = coupon_user.coupon.type.name

                        #setting coupon to order:
                        order.coupon = coupon
                        order.save(force_update=True)
                        order = Order.objects.get(id=order.id)

                        if coupon_type == 'percentage':
                            data["result"] = "success" #for reloading a page in ajax

                        if redeemed:
                            data = {'is_used': True}
                    else:
                        data = {'is_used': True}

                except Exception as err:
                    print(err)
                    print('')
                    data = {'is_used': 'invalid'}
                    pass
    response = data
    return JsonResponse(response)
