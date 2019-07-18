from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from ..models import *
from .serializers import *
from django.db.models import Q
from utils.api_helpers import FilterViewSet


class BlogCategoryViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        qs = BlogCategory.objects.filter(is_active=True)
        return qs


class BlogTagViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = BlogTag.objects.all()
    serializer_class = BlogTagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        qs = BlogTag.objects.filter(is_active=True)
        return qs


class BlogPostViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        qs = BlogPost.objects.filter(is_active=True)
        return qs


class BlogPostTagViewSet(viewsets.ModelViewSet, FilterViewSet):
    queryset = BlogPostTag.objects.all()
    serializer_class = BlogPostTagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get']

    def get_queryset(self):
        qs = BlogPostTag.objects.filter(is_active=True)
        return qs