import django_filters
from ..models import Review

class ReviewFilter(django_filters.FilterSet):
    tourist_user_id = django_filters.NumberFilter(name='order__tourist__user_id')
    guide_user_id = django_filters.NumberFilter(name='order__guide__user_id')

    class Meta:
        model = Review
        fields = {
            'tourist_user_id': ['exact'],
            'guide_user_id': ['exact'],
            'guide_rating': ['exact', 'gte', 'lte'],
            'tourist_rating': ['exact', 'gte', 'lte'],
            'is_guide_feedback': ['exact'],
            'is_tourist_feedback': ['exact'],
        }
