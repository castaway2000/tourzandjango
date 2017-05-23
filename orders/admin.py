from django.contrib import admin
from .models import *


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderStatus._meta.fields]

    class Meta:
        model = OrderStatus

admin.site.register(OrderStatus, OrderStatusAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]

    class Meta:
        model = Order

admin.site.register(Order, OrderAdmin)


class ServiceInOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceInOrder._meta.fields]

    class Meta:
        model = ServiceInOrder

admin.site.register(ServiceInOrder, ServiceInOrderAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]

    class Meta:
        model = Payment

admin.site.register(Payment, PaymentAdmin)