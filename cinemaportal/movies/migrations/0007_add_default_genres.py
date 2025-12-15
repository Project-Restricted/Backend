from django.db import migrations
from django.db.utils import IntegrityError


GENRES = [
    (1, 'Боевик'),
    (2, 'Драма'),
    (3, 'Комедия'),
    (4, 'Фантастика'),
    (5, 'Ужасы'),
    (6, 'Триллер'),
    (7, 'Мелодрама'),
    (8, 'Детектив'),
    (9, 'Приключения'),
    (10, 'Фэнтези'),
    (11, 'Мультфильм'),
]


def forward(apps, schema_editor):
    Genre = apps.get_model('movies', 'Genre')
    for gid, name in GENRES:
        try:
            Genre.objects.update_or_create(pk=gid, defaults={'name': name})
        except IntegrityError:
            # Another row may already have this name (unique constraint). Skip gracefully.
            if Genre.objects.filter(name=name).exists():
                continue
            raise


def backward(apps, schema_editor):
    Genre = apps.get_model('movies', 'Genre')
    for gid, name in GENRES:
        try:
            g = Genre.objects.get(pk=gid)
            if g.name == name:
                g.delete()
        except Genre.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_remove_post_parent_post_liked_by'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
