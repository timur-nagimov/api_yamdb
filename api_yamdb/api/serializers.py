from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                '`me` нельзя использовать в качестве имени!',
            )
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'bio', 'role',
        )


class UserMeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
