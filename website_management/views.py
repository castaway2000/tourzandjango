# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import PageContent
from .forms import ContactUsMessageNotSignedInForm, ContactUsMessageSignedInForm
from django.contrib import messages
from django.utils.translation import ugettext as _


def tos(request):
    tos = PageContent.objects.get(id=1, is_active=True)
    return render(request, 'website_management/tos.html', locals())


def about_us(request):
    about_us = PageContent.objects.get(id=2, is_active=True)
    return render(request, 'website_management/about_us.html', locals())


def privacy_policy(request):
    privacy_policy = PageContent.objects.get(id=3, is_active=True)
    return render(request, 'website_management/privacy_policy.html', locals())


def faq(request):
    return render(request, 'website_management/faq.html', locals())


def contact_us(request):
    user = request.user
    if not user.is_anonymous():
        form = ContactUsMessageSignedInForm(request.POST or None)
    else:
        form = ContactUsMessageNotSignedInForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            new_form = form.save(commit=False)
            if not user.is_anonymous():
                new_form.user = user
                new_form.email = user.email
            new_form = form.save()
            messages.success(request, _('Your message has been successfully delivered!'))
        else:
            messages.error(request, _('There is some error with submiting of your message!'))

    return render(request, 'website_management/contact_us.html', locals())