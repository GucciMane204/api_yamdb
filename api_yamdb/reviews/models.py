from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_year

class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]