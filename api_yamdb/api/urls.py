from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import UserRegistrationView, UserViewSet, TokenObtainView

router = SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', UserRegistrationView.as_view(), name='signup'),
    path('v1/', include(router.urls)),
    path('v1/auth/token/', TokenObtainView.as_view())
]
