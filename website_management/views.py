# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import PageContent


def tos(request):
    tos = PageContent.objects.get(id=1, is_active=True)
    return render(request, 'website_management/tos.html', locals())


def about_us(request):
    about_us = PageContent.objects.get(id=2, is_active=True)
    return render(request, 'website_management/about_us.html', locals())


def privacy_policy(request):
    privacy_policy = PageContent.objects.get(id=3, is_active=True)
    return render(request, 'website_management/privacy_policy.html', locals())


def contact_us(request):
    return render(request, 'website_management/contact_us.html', locals())