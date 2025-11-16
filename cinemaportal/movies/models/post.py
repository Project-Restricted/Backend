from django.db import models
from .movie import Movie
from django.conf import settings

class Post(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
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

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.creation_date.strftime('%Y-%m-%d')}"

    def is_reply(self):
        return self.parent is not None