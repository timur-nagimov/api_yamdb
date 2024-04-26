from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import (
    NAME_LENGTH,
    SLAG_LENGTH,
    ROLE_LENGTH,
    CODE_LENGTH,
    USER_LENGTH
)


class Category(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, verbose_name='Название')
    slug = models.SlugField(
        max_length=SLAG_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, verbose_name='Название')
    slug = models.SlugField(
        max_length=SLAG_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('slug',)

    def __str__(self):
        return self.name


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError('Год выпуска не может быть больше текущего года')


class Title(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, verbose_name='Название')
    year = models.IntegerField(
        validators=(validate_year,), verbose_name='Год выхода')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


def validate_username(value):
    if value == 'me':
        raise ValidationError('Имя пользователя не может быть `me`.')


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User')
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    role = models.CharField(
        max_length=ROLE_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Статус'
    )
    email = models.EmailField(
        'Почтовый адрес',
        unique=True
    )
    confirmation_code = models.CharField(
        'Код авторизации',
        max_length=CODE_LENGTH,
        default='',
        blank=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USER_LENGTH,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя может '
                'содержать только буквы, цифры '
                'и символы @/./+/-/_',
                code='invalid_username',
            ),
            validate_username,
        ),
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moder(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.PositiveIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10)),
        blank=False,
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='author_title_unique'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.text} {self.title.name}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        blank=True,
        related_name='comments',
        verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
