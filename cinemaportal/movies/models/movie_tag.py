from django.db import models
from .movie import Movie
from .tag import Tag


class MovieTag(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
          related_name='movie_tags'
          )
    

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_movies'
        )

    class Meta:
        verbose_name = "Тег фильма"
        verbose_name_plural = "Теги фильмов"
        unique_together = ('movie', 'tag')

    def __str__(self):
        return f"{self.movie.title} — {self.tag.tag}"