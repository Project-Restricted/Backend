from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ('movies', '0007_add_default_genres'),
        ('users', '0002_moderatorrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie_ratings', to='users.user')),
            ],
            options={
                'verbose_name': 'Оценка фильма',
                'verbose_name_plural': 'Оценки фильмов',
                'unique_together': {('movie', 'user')},
            },
        ),
    ]
