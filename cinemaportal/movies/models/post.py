from django.db import models
from .movie import Movie
from django.conf import settings


class Post(models.Model):
    """Flat review model (no tree). Each Post is a review for a Movie.

    Likes are implemented via a ManyToManyField `liked_by` to track users
    who liked the post (prevents duplicate likes by the same user).
    """
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    text = models.TextField(verbose_name="Текст поста")
    creation_date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.creation_date.strftime('%Y-%m-%d')}"

    @property
    def likes(self):
        return self.liked_by.count()