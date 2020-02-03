import os
import sys
if not 'DJANGO_SETTINGS_MODULE' in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tourzan.settings'
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../../")))
    import django
    django.setup()

from orders.models import Order
from django.utils import timezone
from utils.sending_emails import SendingEmail


class GetOrdersPayments():
    """This class is launched by a scheduler"""

    def __init__(self, *args, **kwargs):
        print("Get orders payments: started {}".format(timezone.now().date()))
        self.launch()
        print("Get orders payments: finished")

    def launch(self):
        current_date = timezone.now().date()
        orders = Order.objects.filter(payment_status_id=2, date_booked_for__date=current_date).exclude(status_id__in=[3, 6])

        """Sending function results in email"""
        summary = {"success": {"amount": 0, "nmb": 0},
                   "errors": {"amount": 0, "nmb": 0},
                   "errors_list": list()
                   }
        for order in orders.iterator():
            try:
                order.make_payment(order.tourist.user_id)
                summary["success"]["amount"] += float(order.total_price)
                summary["success"]["nmb"] += 1
            except Exception as e:
                summary["error"]["amount"] += float(order.total_price)
                summary["error"]["nmb"] += 1
                summary["errors_list"].append({"order_id": order.id, "error_text": str(e)})
        SendingEmail().email_orders_payment_batch({"summary": summary})
        return True


if __name__ == '__main__':
    GetOrdersPayments()
