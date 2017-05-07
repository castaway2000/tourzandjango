from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


#tourist profile which is created by default for all users
class TouristProfile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="users/images", blank=True, null=True, default=None)
    about = models.TextField(max_length=5000, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __unicode__(self):
        return "%s" % self.user.username


"""
creating user profile after user is created (mostly for login with Facebook)
"""
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        kwargs = dict()
        kwargs["user"] = instance
        TouristProfile.objects.create(**kwargs)

post_save.connect(create_user_profile, sender=User)
