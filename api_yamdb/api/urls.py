from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GenreViewSet,
    CategoryViewSet,
    TitleViewSet,
    UserRegistrationView,
    UserViewSet,
    TokenObtainView,
    UserMeView,
    ReviewViewSet
)

router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'reviews', ReviewViewSet, basename='reviews')
me_view = UserMeView.as_view({'get': 'retrieve', 'patch': 'partial_update'})

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/categories/<slug:slug>/',
         CategoryViewSet.as_view({'delete': 'perform_destroy'}),
         name='category-destroy'),
    path('v1/genres/<slug:slug>/',
         GenreViewSet.as_view({'delete': 'perform_destroy'}),
         name='genre-destroy'),
    path('v1/titles/<int:title_id>/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='title_reviews'),
    path('v1/titles/<int:title_id>/reviews/<int:pk>/', ReviewViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='review_detail'),
    path('v1/users/me/', me_view, name='user-me'),
    path('v1/auth/signup/', UserRegistrationView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view()),
]