from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class MovieRating(models.Model):
    movie = models.ForeignKey(
        'movies.Movie', on_delete=models.CASCADE, related_name='ratings'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='movie_ratings'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        unique_together = ('movie', 'user')
        verbose_name = 'Оценка фильма'
        verbose_name_plural = 'Оценки фильмов'

    def __str__(self):
        return f"{self.user.username} -> {self.movie.title}: {self.score}"
