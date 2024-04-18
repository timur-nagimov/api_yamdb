from django.db import models
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()


class Title(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )
    genres = models.ManyToManyField(Genre, related_name='titles')


class User(AbstractUser):
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10,
        choices=[('admin', 'Admin'), ('user', 'User')],
        default='user'
    )
    email = models.EmailField(
        'Почтовый адрес',
        unique=True
    )
    confirmation_code = models.CharField(
        'Код авторизации',
        max_length=15,
        null=True,
        blank=True
    )

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
