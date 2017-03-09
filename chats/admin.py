from django.contrib import admin
from .models import *


class ChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Chat._meta.fields]

    class Meta:
        model = Chat

admin.site.register(Chat, ChatAdmin)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChatMessage._meta.fields]

    class Meta:
        model = ChatMessage

admin.site.register(ChatMessage, ChatMessageAdmin)