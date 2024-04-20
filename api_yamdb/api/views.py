from rest_framework import mixins, viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import MethodNotAllowed
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review
from .serializers import (
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    TokenObtainSerializer,
    UserMeSerializer,
    ReviewSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOrDeny, AllowGetOrIsAdminOrDeny, IsAuthorOrHasAccess
from .email_utils import email_generator

User = get_user_model()


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowGetOrIsAdminOrDeny,)
    pagination_class = LimitOffsetPagination
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
    permission_classes = (AllowGetOrIsAdminOrDeny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, instance):
        super(GenreViewSet, self).perform_destroy(instance)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (AllowGetOrIsAdminOrDeny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'year', 'category__name', 'genre__name')
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')


class UserRegistrationView(APIView):

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if User.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
            email_generator(request.data.get('username'))
            return Response(request.data, status=status.HTTP_200_OK)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        email_generator(request.data.get('username'))
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrDeny, IsAdminOrReadOnly)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    http_method_names = ('get', 'post', 'patch', 'delete',)


class UserMeView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = UserMeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    http_method_names = ('get', 'patch')

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get()
        self.check_object_permissions(self.request, obj)
        return obj


class TokenObtainView(APIView):
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            # Извлечение токена из сериализатора
            username = serializer.data['username']
            token = serializer.validated_data['confirmation_code']
            user = get_object_or_404(User, username=username)
            if token != user.confirmation_code:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

