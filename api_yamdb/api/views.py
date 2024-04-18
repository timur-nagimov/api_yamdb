from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer, TokenObtainSerializer
from django.core.mail import send_mail

from .email_utils import email_generator

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


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
