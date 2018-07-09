
import django_filters
from ..models import GuideProfile


class GuideFilter(django_filters.FilterSet):
    guide = django_filters.CharFilter(name='user__generalprofile__first_name')
    rate = django_filters.NumberFilter(name='rate')
    rating = django_filters.NumberFilter(name='rating')
    show_only_verified = django_filters.BooleanFilter(name='user__generalprofile__is_verified')

    class Meta:
        model = GuideProfile
        fields = {
            'guide': ['exact', 'contains'],
            'rate': ['exact', 'gte', 'lte'],
            'rating': ['exact', 'gte', 'lte'],
            'show_only_verified': ['exact'],
        }