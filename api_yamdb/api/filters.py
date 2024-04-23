from django_filters import FilterSet, CharFilter

from reviews.models import Title


def filter_by_slug(queryset, name, value):
    return queryset.filter(**{f'{name}__slug': value})


class TitleFilter(FilterSet):
    genre = CharFilter(method=filter_by_slug)
    category = CharFilter(method=filter_by_slug)
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
