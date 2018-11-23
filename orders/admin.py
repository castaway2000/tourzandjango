from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


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


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order


class OrderAdmin(ImportExportModelAdmin):#admin.ModelAdmin):
    resource_class = OrderResource
    list_display = [field.name for field in Order._meta.fields]

    class Meta:
        model = Order

admin.site.register(Order, OrderAdmin)


class OrderStatusChangeHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderStatusChangeHistory._meta.fields]

    class Meta:
        model = OrderStatusChangeHistory

admin.site.register(OrderStatusChangeHistory, OrderStatusChangeHistoryAdmin)


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


class OtherReviewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OtherReviews._meta.fields]

    class Meta:
        model = OtherReviews

admin.site.register(OtherReviews, OtherReviewsAdmin)