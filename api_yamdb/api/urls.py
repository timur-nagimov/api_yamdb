from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet

router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
     path('v1/categories/<slug:slug>/',
         CategoryViewSet.as_view({'delete': 'perform_destroy'}),
         name='category-destroy'),
    path('v1/genres/<slug:slug>/',
         GenreViewSet.as_view({'delete': 'perform_destroy'}),
         name='genre-destroy'),
    ]