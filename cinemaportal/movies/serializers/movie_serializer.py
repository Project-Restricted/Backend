# movies/serializers/movie_serializer.py
from rest_framework import serializers
from movies.models.movie import Movie

class MovieListSerializer(serializers.ModelSerializer):
    """
    FilmPreview: id, title, posterUrl, year, duration (number), rating, genres (string[])
    duration возвращаем в минутах (int). Если нужна другая единица — поменяем.
    """
    posterUrl = serializers.URLField(source='poster_url', allow_null=True)
    rating = serializers.FloatField()
    duration = serializers.SerializerMethodField()

    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Movie
        fields = ['id', 'title', 'posterUrl', 'year', 'duration', 'rating', 'genres']

    def get_duration(self, obj):
        """
        Возвращаем продолжительность в минутах (int).
        Модель хранит DurationField (timedelta) — для фронта удобнее минуты.
        Если нужно секунды — заменить на total_seconds().
        """
        d = getattr(obj, 'duration', None)
        if not d:
            return None
        total_seconds = int(d.total_seconds())
        minutes = total_seconds // 60
        return minutes
