from django.contrib import admin
from .models import *


class PaymentCustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentCustomer._meta.fields]

    class Meta:
        model = PaymentCustomer

admin.site.register(PaymentCustomer, PaymentCustomerAdmin)


class PaymentMethodTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentMethodType._meta.fields]

    class Meta:
        model = PaymentMethodType

admin.site.register(PaymentMethodType, PaymentMethodTypeAdmin)


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentMethod._meta.fields]

    class Meta:
        model = PaymentMethod

admin.site.register(PaymentMethod, PaymentMethodAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]

    class Meta:
        model = Payment

admin.site.register(Payment, PaymentAdmin)