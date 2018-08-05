from rest_framework.decorators import api_view
from django.http import JsonResponse
from pyfcm import FCMNotification
from txfcm import TXFCMNotification
from twisted.internet import reactor

import json

from tourzan.settings import FCM_API_KEY


@api_view(['POST'])
def push_notify_one(request):
    try:
        device_id = str(request.POST['device_id'])
        msg_title = str(request.POST['title'])
        msg_body = str(request.POST['body'])
        fcm_push_service = FCMNotification(api_key=FCM_API_KEY)
        result = fcm_push_service.notify_single_device(registration_id=device_id, message_title=msg_title,
                                                       message_body=msg_body)
        return JsonResponse(json.dumps({'status': 200, 'detail': str(result)}))
    except Exception as err:
        return JsonResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))


@api_view(['POST'])
def push_notify_many(request):
    try:
        # device_id_list = list(request.POST['device_id'])
        # msg_title = str(request.POST['title'])
        # msg_body = str(request.POST['body'])
        #
        # txf_push_service = TXFCMNotification(api_key=FCM_API_KEY)
        # df = txf_push_service.notify_multiple_devices(registration_ids= device_id_list, message_title=msg_title,
        #                                               message_body=msg_body)
        #
        # def got_result(result):
        #     print(result)
        # df.addBoth(got_result)
        # reactor.run()
        df = 'not in service'
        return JsonResponse(json.dumps({'status': 200, 'detail': str(df)}))
    except Exception as err:
        return JsonResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))
