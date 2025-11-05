from django.db import models


class Tag(models.Model):
    """
    Таблица тегов. 
    Тег — это уникальная метка, которую можно прикреплять к фильмам.
    """
    tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.tag