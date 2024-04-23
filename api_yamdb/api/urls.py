from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GenreViewSet,
    CategoryViewSet,
    TitleViewSet,
    UserRegistrationView,
    UserViewSet,
    TokenObtainView,
    ReviewViewSet,
    CommentViewSet
)

router_v1 = DefaultRouter()

router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'users', UserViewSet, basename='users')

# me_view = UserMeView.as_view({'get': 'retrieve', 'patch': 'partial_update'})

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    # path('v1/users/me/', me_view, name='user-me'),
    path('v1/', include(router_v1.urls)),

    path('v1/auth/signup/', UserRegistrationView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view()),
]
