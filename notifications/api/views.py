from rest_framework.decorators import api_view
from django.http import HttpResponse
from pyfcm import FCMNotification
import json

from tourzan.settings import FCM_API_KEY


@api_view(['POST'])
def push_notify_one(request):
    try:
        device_ids = [str(request.POST['device_id'])]
        msg_title = str(request.POST['title'])
        msg_body = str(request.POST['body'])
        fcm_push_service = FCMNotification(api_key=FCM_API_KEY)
        result = fcm_push_service.notify_multiple_devices(registration_ids=device_ids, message_title=msg_title,
                                                          message_body=msg_body)
        print(result)
        return HttpResponse(json.dumps({'status': 200, 'detail': str(result)}))
    except Exception as err:
        return HttpResponse(json.dumps({'errors': [{'status': 400, 'detail': str(err)}]}))