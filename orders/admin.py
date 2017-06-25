from django.contrib import admin
from .models import *


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderStatus._meta.fields]

    class Meta:
        model = OrderStatus

admin.site.register(OrderStatus, OrderStatusAdmin)


class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentStatus._meta.fields]

    class Meta:
        model = PaymentStatus

admin.site.register(PaymentStatus, PaymentStatusAdmin)


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


class ReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Review._meta.fields]

    class Meta:
        model = Review

admin.site.register(Review, ReviewAdmin)