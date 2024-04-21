from rest_framework import serializers
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import status
from django.db.models import Avg

from reviews.models import Category, Genre, Title, Review, TitleGenre

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)
    slug = serializers.SlugField(required=True, max_length=50)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError(
                {'slug': 'This slug already exists.'}, code='invalid')

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=256)
    slug = serializers.SlugField(required=True, max_length=50)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError(
                {'slug': 'This slug already exists.'}, code='invalid')

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategoryField(serializers.RelatedField):
    def to_internal_value(self, data):
        try:
            return Category.objects.get(name=data)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                f"Category with name '{data}' does not exist.")

    def to_representation(self, value):
        serializer = CategorySerializer(value)
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
                f"Genre with name '{data}' does not exist.")


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True, max_length=256, label='Название')
    year = serializers.IntegerField(required=True, label='Год выпуска')
    genre = StringToGenreField(many=True)
    category = CategoryField(queryset=Category.objects.all())
    rating = SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre_data in genres_data:
            current_genre, status = Genre.objects.get_or_create(
                name=genre_data)
            TitleGenre.objects.create(genre=current_genre, title=title)
        return title

    def get_rating(self, obj):
        reviews = obj.review_set.all()
        average_rating = reviews.aggregate(Avg('score'))['score__avg']

        if average_rating is None:
            return 0

        return round(average_rating, 2)


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
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = User.objects.filter(username=username).first()

        if user and user.confirmation_code == confirmation_code:
            return data
        else:
            raise serializers.ValidationError(
                "Invalid username or confirmation code")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
