from rest_framework import serializers
from django.conf import settings

from movies.models import Movie, Post
from users.models import User


# --- Вспомогательный сериализатор для юзера в отзывах ---
class UserBriefSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatarUrl']

    def get_avatarUrl(self, obj):
        request = self.context.get('request')
        if getattr(obj, 'avatar_url', None):
            return obj.avatar_url
        return None


# --- Сериализатор отзыва (чтение) ---
class ReviewSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    createdAt = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    likedByCurrentUser = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'text',
            'createdAt',
            'user',
            'likes',
            'likedByCurrentUser',
        ]

    def get_createdAt(self, obj):
        return int(obj.creation_date.timestamp())

    def get_likes(self, obj):
        # likes property on model returns liked_by.count()
        return getattr(obj, 'likes', 0)

    def get_likedByCurrentUser(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return obj.liked_by.filter(pk=user.pk).exists()


# --- Сериализатор отзыва (создание) ---
class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['movie', 'text']

    def create(self, validated_data):
        # автоматически устанавливаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# --- Главный сериализатор фильма ---
class MovieDetailSerializer(serializers.ModelSerializer):
    posterUrl = serializers.SerializerMethodField()
    videoUrl = serializers.SerializerMethodField()

    genres = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()

    duration = serializers.SerializerMethodField()       # минуты
    reviews = serializers.SerializerMethodField()

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
        return obj.video_url

    # --- genres as list of names ---
    def get_genres(self, obj):
        return [g.name for g in obj.genres.all()]

    # --- tags as list of names ---
    def get_tags(self, obj):
        return [t.tag for t in obj.tags.all()]

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

    def get_reviews(self, obj):
        request = self.context.get('request')
        # allow caller to control how many top-level reviews to include
        default_limit = 5
        limit = default_limit
        if request:
            try:
                limit = int(request.query_params.get('reviews_limit', default_limit))
            except (TypeError, ValueError):
                limit = default_limit

        top_level = obj.posts.filter(deleted=False).order_by('-creation_date')[:limit]
        return ReviewSerializer(top_level, many=True, context=self.context).data
