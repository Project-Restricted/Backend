from django.db import models

class Genre(models.Model):

    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name


class MovieGenre(models.Model):

    movie = models.ForeignKey(
        "movies.Movie",  
        on_delete=models.CASCADE,
        related_name='movie_genres'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre_movies'
    )

    class Meta:
        verbose_name = "Жанр фильма"
        verbose_name_plural = "Жанры фильмов"
        unique_together = ('movie', 'genre')

    def __str__(self):
        return f"{self.movie.title} — {self.genre.name}"