from django.db import models


class Tag(models.Model):

    tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.tag