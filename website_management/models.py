# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class PageContent(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name


class ContactUsMessage(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)#for cases when it is send by registered user
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    email = models.EmailField(blank=True, null=True, default=None)
    message = models.TextField(blank=True, null=True, default=None)
    is_read = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.user:
            return "%s" % self.user.username
        else:
            return "%s" % self.name