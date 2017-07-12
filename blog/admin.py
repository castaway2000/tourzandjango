from django.contrib import admin
from .models import *
from django_summernote.admin import SummernoteModelAdmin


class BlogPostAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in BlogPost._meta.fields]

    class Meta:
        model = BlogPost

admin.site.register(BlogPost, BlogPostAdmin)


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BlogCategory._meta.fields]

    class Meta:
        model = BlogCategory

admin.site.register(BlogCategory, BlogCategoryAdmin)


class BlogTagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BlogTag._meta.fields]

    class Meta:
        model = BlogTag

admin.site.register(BlogTag, BlogTagAdmin)


class BlogPostTagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BlogPostTag._meta.fields]

    class Meta:
        model = BlogPostTag

admin.site.register(BlogPostTag, BlogPostTagAdmin)