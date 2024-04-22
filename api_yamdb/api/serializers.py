from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
                f'Жанр `{data}` не существует.')


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    category = CategoryField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = GenreField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        allow_empty=False,
        many=True
    )
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

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

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)
        if confirmation_code != user.confirmation_code:
            raise ValidationError(
                {'confirmation_code': 'Invalid confirmation code.'})

        data['user'] = user
        return data


class ReviewSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(min_value=1, max_value=10)
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        user = self.context.get('request').user

        if self.Meta.model.objects.filter(
                title_id=title_id,
                author=user).exists():
            raise ValidationError('Вы не можете оставлять более одного '
                                  'отзыва на одно произведение!')

        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
