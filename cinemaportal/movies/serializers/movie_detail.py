from rest_framework import serializers
from django.conf import settings

from movies.models import Movie, Post
from users.models import User


# --- Вспомогательный сериализатор для юзера в отзывах ---
class UserBriefSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.SerializerMethodField()
    username = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'username', 'avatarUrl']

    def get_avatarUrl(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


# --- Сериализатор отзыва ---
class ReviewSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    replyOn = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'replyOn',
            'text',
            'likes',
            'createdAt',
            'user'
        ]

    def get_replyOn(self, obj):
        return obj.reply_on_id  # int или None

    def get_createdAt(self, obj):
        return int(obj.created_at.timestamp())


# --- Главный сериализатор фильма ---
class MovieDetailSerializer(serializers.ModelSerializer):
    posterUrl = serializers.SerializerMethodField()
    videoUrl = serializers.SerializerMethodField()

    genres = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()

    duration = serializers.SerializerMethodField()       # минуты
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id',
            'title',
            'posterUrl',
            'country',
            'year',
            'duration',
            'genres',
            'tags',
            'director',
            'actors',
            'description',
            'rating',
            'videoUrl',
            'reviews'
        ]

    # --- poster absolute URL ---
    def get_posterUrl(self, obj):
        if not obj.poster_url:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(obj.poster_url)

    # --- video absolute URL ---
    def get_videoUrl(self, obj):
        if not obj.video_url:
            return None
        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(obj.poster_url)

    # --- genres as list of names ---
    def get_genres(self, obj):
        return [g.name for g in obj.genres.all()]

    # --- tags as list of names ---
    def get_tags(self, obj):
        return [t.name for t in obj.tags.all()]

    # --- actors formatted красиво ---
    def get_actors(self, obj):
        return [str(a) for a in obj.actors.all()]   # __str__ в модели актёра

    # --- director (если один) ---
    def get_director(self, obj):
        directors = obj.directors.all()
        if not directors:
            return None
        return ", ".join(str(d) for d in directors)

    # --- длительность в минутах ---
    def get_duration(self, obj):
        if not obj.duration:
            return None
        return int(obj.duration.total_seconds() // 60)
