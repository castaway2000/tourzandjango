from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from utils.uploadings import upload_path_handler_tourist_profile_image, upload_path_handler_tourist_travel_pictures
from utils.images_resizing import optimize_size


#tourist profile which is created by default for all users
class TouristProfile(models.Model):
    user = models.OneToOneField(User)
    rating = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image = models.ImageField(upload_to=upload_path_handler_tourist_profile_image, blank=True, null=True, default=None)
    about = models.TextField(max_length=5000, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username

    def __init__(self, *args, **kwargs):
        super(TouristProfile, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if self._original_fields["image"] != self.image:
            self.image = optimize_size(self.image, "medium")
        super(TouristProfile, self).save(*args, **kwargs)


class TouristTravelPhoto(models.Model):
    user = models.ForeignKey(User)
    image = models.ImageField(upload_to=upload_path_handler_tourist_travel_pictures)
    order = models.ForeignKey("orders.Order", blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.user.username


    def __init__(self, *args, **kwargs):
        super(TouristTravelPhoto, self).__init__(*args, **kwargs)

        self._original_fields = {}
        for field in self._meta.get_fields(include_hidden=True):
            try:
                self._original_fields[field.name] = getattr(self, field.name)
            except:
                pass

    def save(self, *args, **kwargs):
        if self._original_fields["image"] != self.image:
            self.image = optimize_size(self.image, "large")
        super(TouristTravelPhoto, self).save(*args, **kwargs)


