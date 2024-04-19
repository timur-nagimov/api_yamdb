from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, filters, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import Review, Comment
from .email_utils import email_generator
from .permissions import IsAdminOrDeny
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    TokenObtainSerializer,
    UserMeSerializer,
    ReviewSerializer,
    CommentSerializer
)


User = get_user_model()


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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Опционально: фильтрация комментариев по id отзыва.
        """
        queryset = super().get_queryset()
        review_id = self.request.query_params.get('review_id')
        if review_id:
            queryset = queryset.filter(review__id=review_id)
        return queryset
