from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import mixins, viewsets, filters, status, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.tokens import RefreshToken

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
    CommentSerializer,
    User
)
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminOrDeny,
    AllowGetOrIsAdminOrDeny,
    IsAuthorOrHasAccess,
)
from .filters import TitleFilter
from .email_utils import email_generator


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowGetOrIsAdminOrDeny,)
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
        Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitleSerializer
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filterset_class = TitleFilter


class UserRegistrationView(APIView):

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        serializer = UserRegistrationSerializer(data=request.data)
        if User.objects.filter(username=username,
                               email=email).exists():
            email_generator(username)
            return Response(request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        email_generator(username)
        return Response(serializer.data)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrDeny,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(detail=False, methods=('get', 'patch'), url_path='me',
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=UserMeSerializer)
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(
            user, data=request.data, partial=True)

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TokenObtainView(APIView):

    def post(self, request):
        serializer = TokenObtainSerializer(
            data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        token = RefreshToken.for_user(user)
        return Response(
            {'token': str(token.access_token)},
            status=status.HTTP_200_OK
        )


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrHasAccess,)
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(
            Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrHasAccess,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')

        return get_object_or_404(Review, pk=review_id, title_id=title_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
