from django.contrib import admin
from .models import *


class EmailMessageTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EmailMessageType._meta.fields]

    class Meta:
        model = EmailMessageType

admin.site.register(EmailMessageType, EmailMessageTypeAdmin)


class EmailMessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EmailMessage._meta.fields]

    class Meta:
        model = EmailMessage

admin.site.register(EmailMessage, EmailMessageAdmin)