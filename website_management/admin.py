# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import *


class HomePageContentAdmin(SummernoteModelAdmin):

    class Meta:
            model = HomePageContent

admin.site.register(HomePageContent, HomePageContentAdmin)


class PageContentAdmin(SummernoteModelAdmin):

    class Meta:
            model = PageContent

admin.site.register(PageContent, PageContentAdmin)


class ContactUsMessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ContactUsMessage._meta.fields]
    class Meta:
            model = ContactUsMessage

admin.site.register(ContactUsMessage, ContactUsMessageAdmin)
