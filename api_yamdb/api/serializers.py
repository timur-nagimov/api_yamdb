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
        
