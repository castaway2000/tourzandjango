from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from coupons.models import Coupon, CouponUser


@login_required()
def coupon_validation(request):
    coupon_code = request.GET.get('coupon', None)
    user = request.user
    print(coupon_code)
    data = {'is_used': 'invalid'}
    if coupon_code:
        coupon_code = coupon_code.strip()
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.get_if_more_users_available():
                coupon_user, created = CouponUser.objects.get_or_create(user_id=user.id, coupon=coupon)
                redeemed = coupon_user.redeemed_at
                discount = coupon_user.coupon.value
                coupon_type = coupon_user.coupon.type.name
                data = {'is_used': False}
                if coupon_type == 'percent':
                    data['fancy_discount'] = '${} off'.format(discount)
                if redeemed:
                    data = {'is_used': True}
            else:
                data = {'is_used': True}

        except Exception as err:
            print(err)
            print('')
            data = {'is_used': 'invalid'}
            pass
    print(data)
    response = data
    return JsonResponse(response)
