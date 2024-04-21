from rest_framework import mixins, viewsets, filters, status, permissions
from rest_framework.response import Response
from django.db.models import Avg
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
    ReviewSerializer,
    CommentSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOrDeny, AllowGetOrIsAdminOrDeny, IsAuthorOrHasAccess, HasPrevilegesOrReadOnly
from .filters import TitleFilter
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


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AllowGetOrIsAdminOrDeny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')).order_by('name')

    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitleSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)

    filterset_class = TitleFilter


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
    permission_classes = (IsAdminOrDeny,)

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
            username = serializer.validated_data['username']
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
    permission_classes = (IsAuthorOrHasAccess,)
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrHasAccess,)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
