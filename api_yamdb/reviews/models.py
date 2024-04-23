from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import NAME_LENGTH, SLAG_LENGTH, ROLE_LENGTH, CODE_LENGTH


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


class Title(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, verbose_name='Название')
    year = models.IntegerField(verbose_name='Год выхода')
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

    def clean(self):
        if self.year < 0:
            raise ValidationError(
                'Год выпуска не может быть отрицательным числом'
            )
        elif self.year > timezone.now().year:
            raise ValidationError(
                'Год выпуска не может быть больше текущего года'
            )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


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

    def clean(self):
        super().clean()
        if self.username == 'me':
            raise ValidationError(
                '`me` нельзя использовать в качестве имени!'
            )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moder(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

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
        validators=[MinValueValidator(1), MaxValueValidator(10)],
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
                fields=['author', 'title'], name='author_title_unique'
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
