# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from utils.images_resizing import optimize_size
from utils.uploadings import (upload_path_handler_homepage, upload_path_handler_homepage_large,
                                upload_path_handler_homepage_medium, upload_path_handler_homepage_small)


class HomePageContent(models.Model):
    motto = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=upload_path_handler_homepage, blank=True, null=True, default=None)
    image_large = models.ImageField(upload_to=upload_path_handler_homepage_large, blank=True, null=True, default=None)
    image_medium = models.ImageField(upload_to=upload_path_handler_homepage_medium, blank=True, null=True, default=None)
    image_small = models.ImageField(upload_to=upload_path_handler_homepage_small, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

    def __init__(self, *args, **kwargs):
        super(HomePageContent, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if self._original_fields["image"] != self.image or (self.image and (not self.image_large or not self.image_medium or not self.image_small)):
            self.image_large = optimize_size(self.image, "large")
            self.image_medium = optimize_size(self.image, "medium")
            self.image_small = optimize_size(self.image, "small")
        super(HomePageContent, self).save(*args, **kwargs)


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