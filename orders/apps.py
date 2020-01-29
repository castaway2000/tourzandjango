from __future__ import unicode_literals
from django.conf import settings
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'orders'

    def ready(self):
        print("orders app ready")
        from . import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()
