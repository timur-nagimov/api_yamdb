from rest_framework import mixins, viewsets, filters, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Category, Genre
from .serializers import CategorySerializer, GenreSerializer
from .permissions import IsAdminOrReadOnly

class CategoryViewSet(mixins.CreateModelMixin, 
                      mixins.ListModelMixin, 
                      mixins.DestroyModelMixin, 
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, instance):
        super(CategoryViewSet, self).perform_destroy(instance)


class GenreViewSet(mixins.CreateModelMixin, 
                      mixins.ListModelMixin, 
                      mixins.DestroyModelMixin, 
                      viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, instance):
        super(GenreViewSet, self).perform_destroy(instance)
    
