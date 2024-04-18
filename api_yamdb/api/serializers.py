import datetime

from rest_framework import serializers


from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)

    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)

    class Meta:
        model = Genre
        fields = '__all__'
        

class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    genre = serializers.ListField(child=serializers.CharField(),required=True)
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all(), required=True)

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        current_year = datetime.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError('Год выпуска не может быть больше текущего года.')
        return value

    def validate_genre(self, value):
        for genre_slug in value:
            if not Genre.objects.filter(slug=genre_slug).exists():
                raise serializers.ValidationError(f"Жанр с slug '{genre_slug}' не существует.")
        return value

    def validate_category(self, value):
        if not Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError(f"Категория с slug '{value}' не существует.")
        return value
