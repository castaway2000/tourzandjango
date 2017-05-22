# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import *


class PageContentAdmin(SummernoteModelAdmin):

    class Meta:
            model = PageContent

admin.site.register(PageContent, PageContentAdmin)
