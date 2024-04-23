import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime

from reviews.models import Category, Genre, Title, User, Review, Comment


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_PATH
        self.import_categories(os.path.join(csv_path, 'category.csv'))
        self.import_genres(os.path.join(csv_path, 'genre.csv'))
        self.import_users(os.path.join(csv_path, 'users.csv'))
        self.import_titles(os.path.join(csv_path, 'titles.csv'))
        self.import_reviews(os.path.join(csv_path, 'review.csv'))
        self.import_comments(os.path.join(csv_path, 'comments.csv'))
        self.import_genre_titles(os.path.join(csv_path, 'genre_title.csv'))

    def import_categories(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    Category.objects.update_or_create(
                        id=row['id'],
                        defaults={'name': row['name'], 'slug': row['slug']}
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обновлении категории {row["name"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован category.csv'))

    def import_genres(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    Genre.objects.update_or_create(
                        id=row['id'],
                        defaults={'name': row['name'], 'slug': row['slug']}
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обновлении жанра {row["name"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован genre.csv'))

    def import_titles(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    category = Category.objects.get(id=row['category'])
                    Title.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'name': row['name'],
                            'category': category
                        }
                    )
                except Category.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Категория не найдена: {row["category"]}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обновлении титула {row["name"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован titles.csv'))

    def import_users(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    User.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'username': row['username'],
                            'email': row['email'],
                            'role': row['role'],
                            'bio': row.get('bio', ''),
                            'first_name': row.get('first_name', ''),
                            'last_name': row.get('last_name', '')
                        }
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        'Ошибка при обновлении пользователя'
                        f'{row["username"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован users.csv'))

    def import_reviews(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                    Review.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'title': title,
                            'text': row['text'],
                            'author': author,
                            'score': row['score'],
                            'pub_date': parse_datetime(row['pub_date'])
                        }
                    )
                except (Title.DoesNotExist, User.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обновлении отзыва {row["id"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован review.csv'))

    def import_comments(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                    Comment.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'review': review,
                            'text': row['text'],
                            'author': author,
                            'pub_date': parse_datetime(row['pub_date'])
                        }
                    )
                except (Review.DoesNotExist, User.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Ошибка при обновлении комментария {row["id"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован comments.csv'))

    def import_genre_titles(self, filename):
        try:
            file = open(filename, encoding='utf-8')
        except IOError as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при открытии файла {filename}: {e}'))
            return

        with file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genres.add(genre)
                except (Title.DoesNotExist, Genre.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        'Ошибка при добавлении жанра к титулу '
                        f'{row["title_id"]}: {e}'))

        self.stdout.write(self.style.SUCCESS('Импортирован genre_titles.csv'))
