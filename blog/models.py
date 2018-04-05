from __future__ import unicode_literals
from django.contrib.sitemaps import ping_google
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from utils.uploadings import upload_path_handler_blog
from django.utils.text import slugify
import uuid
import unidecode
from utils.general import random_string_creating
from crequest.middleware import CrequestMiddleware
from utils.images_resizing import optimize_size


class BlogCategory(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'BlogCategory'
        verbose_name_plural = 'BlogCategories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(BlogCategory, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    author = models.ForeignKey(User, blank=True, null=True, default=None, related_name="blog_post_author")
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    tags = models.CharField(max_length=256, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating, unique=True)
    text = models.TextField(blank=True, null=True, default=None)
    category = models.ForeignKey(BlogCategory, blank=True, null=True, default=None)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to=upload_path_handler_blog, blank=True, null=True, default="defaults/blog_post_default.jpg")
    is_image_optimized = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, blank=True, null=True, default=None, related_name="blog_post_updated_by")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'BlogPost'
        verbose_name_plural = 'BlogPosts'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        #transforming text tags with ";" separator to BlogTag instances
        if self.tags:
            tags = self.tags.split("; ")
            if tags:
                for tag in tags:
                    tag, created = BlogTag.objects.get_or_create(name=tag)
                    BlogPostTag.objects.get_or_create(blog_post = self, tag=tag, is_active=True)


        #assigning user which edited a blog post
        current_request = CrequestMiddleware.get_request()
        user = current_request.user
        self.updated_by = user

        if not self.pk:
            self.author = user

        if self.image and not self.is_image_optimized:
            try:
                self.image = optimize_size(self.image, "medium")
                self.is_image_optimized = True
            except:
                pass
        super(BlogPost, self).save(*args, **kwargs)
        try:
            ping_google()
        except Exception:
            pass

    def get_absolute_url(self):
        return '/en/blog_post/%s' % self.slug
        # return reverse('post', kwargs={'slug': self.slug})


class BlogTag(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    slug = models.SlugField(blank=True, null=True, default=random_string_creating, unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'BlogTag'
        verbose_name_plural = 'BlogTags'

    def save(self, *args, **kwargs):
        # self.slug = slugify(unidecode.unidecode(self.name))
        self.slug = slugify(self.name)
        super(BlogTag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'slug': self.slug})


class BlogPostTag(models.Model):
    blog_post = models.ForeignKey(BlogPost)
    tag = models.ForeignKey(BlogTag)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return '%s' % self.tag.name

    class Meta:
        verbose_name = 'BlogPostTag'
        verbose_name_plural = 'BlogPostTags'

    def save(self, *args, **kwargs):
        super(BlogPostTag, self).save(*args, **kwargs)