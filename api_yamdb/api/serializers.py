from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    lookup_field = 'slug'

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategoryField(serializers.SlugRelatedField):

    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class StringToGenreField(serializers.StringRelatedField):
    def to_representation(self, value):
        return {
            'name': value.name,
            'slug': value.slug
        }

    def to_internal_value(self, data):
        try:
            return Genre.objects.get(name=data)
        except Genre.DoesNotExist:
            raise serializers.ValidationError(
                f"Жанр '{data}' не существует.")


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    category = CategoryField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )
    genre = GenreField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список жанров не может быть пустым'
            )
        return value

    class Meta:
        model = Title
        fields = '__all__'


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


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True)
    score = serializers.IntegerField(min_value=1, max_value=10, required=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('__all__')
        read_only_fields = ('title', 'author')

    def validate(self, data):
        title = get_object_or_404(
            Title, id=self.context['view'].kwargs.get('title_id'))
        if (
            self.context.get('request').method != 'PATCH'
            and title.reviews.filter(
                author=self.context.get('request').user
            ).exists()
        ):
            raise ValidationError('Вы не можете оставлять более'
                                  'одного отзыва на одно произведение!')

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)
