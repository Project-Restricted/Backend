from django.db import models
from django.conf import settings
from .movie import Movie


class UserRequest(models.Model):
    REQUEST_TYPES = [
        ('movie', 'Добавление фильма'),
        ('tag', 'Добавление тега'),
    ]

    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    type = models.CharField(
        max_length=10,
        choices=REQUEST_TYPES,
        verbose_name="Тип запроса"
    )

    target_movie = models.ForeignKey(
        Movie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_requests",
        verbose_name="Целевой фильм (если есть)"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_requests",
        verbose_name="Автор запроса"
    )

    # хранит данные, присланные от фронтенда (в json-формате)
    data = models.JSONField(
        verbose_name="Данные запроса",
        help_text="Содержимое заявки в формате JSON"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    moderator_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий модератора"
    )

    def __str__(self):
        return f"{self.get_type_display()} от {self.created_by} ({self.status})"

    class Meta:
        verbose_name = "Запрос пользователя"
        verbose_name_plural = "Запросы пользователей"
        ordering = ['-created_at']
