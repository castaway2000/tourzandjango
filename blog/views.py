from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
from .models import *
from tours.models import Tour
from guides.models import GuideProfile
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count


def blog(request):
    categories = BlogCategory.objects.filter(is_active=True).annotate(posts_nmb=Count("blogpost")).order_by("-posts_nmb")[:5]
    tags = BlogTag.objects.filter(is_active=True).annotate(posts_nmb=Count("blogposttag")).order_by("-posts_nmb")[:5]
    blog_posts = BlogPost.objects.filter(is_active=True).order_by("-id").values()


    page = request.GET.get('page', 1)
    paginator = Paginator(blog_posts, 10)
    try:
        blog_posts = paginator.page(page)
    except PageNotAnInteger:
        blog_posts = paginator.page(1)
    except EmptyPage:
        blog_posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/blog.html', locals())


def blog_post(request, slug):
    categories = BlogCategory.objects.filter(is_active=True).annotate(posts_nmb=Count("blogpost")).order_by("-posts_nmb")[:5]
    tags = BlogTag.objects.filter(is_active=True).annotate(posts_nmb=Count("blogposttag")).order_by("-posts_nmb")[:5]
    blog_post = BlogPost.objects.get(slug=slug)
    blog_posts = BlogPost.objects.filter(is_active=True).order_by("-id").values()[:5]

    return render(request, 'blog/blog_post.html', locals())