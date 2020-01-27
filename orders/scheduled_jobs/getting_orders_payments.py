from orders.models import Order
from django.utils import timezone


class GetOrdersPayments():
    """This class is launched by a scheduler"""

    def __init__(self, *args, **kwargs):
        print("Get orders payments: started {}".format(timezone.now().date()))
        self.launch()
        print("Get orders payments: finished")

    def launch(self):
        current_date = timezone.now().date()
        orders = Order.objects.filter(payment_status_id=2, date_booked_for__date=current_date).exclude(status_id__in=[3, 6])
        print(orders)
        for order in orders.iterator():
            order.make_payment(order.tourist.user_id)


if __name__ == '__main__':
    GetOrdersPayments()