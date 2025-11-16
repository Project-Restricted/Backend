from django.db import models
from django.conf import settings
from .country import Country


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    poster_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Продолжительность",
        help_text="Продолжительность фильма в формате ЧЧ:ММ:СС"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movies'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_movies'
    )

    directors = models.ManyToManyField(
        "Director",
        through='MovieDirector',
        related_name='movies',
        blank=True
    )

    genres = models.ManyToManyField(
        "Genre",
        through='MovieGenre',
        related_name='movies',
        blank=True
    )

    actors = models.ManyToManyField(
        "Actor",
        through='MovieActor',
        related_name='movies',
        blank=True
    )

    tags = models.ManyToManyField(
        "Tag",
        through='MovieTag',
        related_name='movies',
        blank=True
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=False,
        default=0,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def main_director(self):
        return self.directors.first()

    @property
    def main_actors(self):
        return self.actors.all()[:5]

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['year', 'rating']),
            models.Index(fields=['approved', 'year']),
        ]


class MovieSource(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='sources'
    )
    source_url = models.TextField(verbose_name="URL источника")

    def __str__(self):
        return f"{self.movie.title} - {self.source_url[:50]}"
