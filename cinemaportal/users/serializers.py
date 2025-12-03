from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичного представления пользователя, возвращает
    поля в формате, который ожидает фронтенд (camelCase).
    """
    avatarUrl = serializers.URLField(source='avatar_url', allow_null=True)
    isModerator = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    averageRating = serializers.SerializerMethodField()
    reviewsCount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'avatarUrl', 'averageRating', 'reviewsCount', 'isModerator', 'createdAt']

    def get_isModerator(self, obj):
        return getattr(obj, 'role', None) == 'moderator'

    def get_createdAt(self, obj):
        dt = getattr(obj, 'created_at', None)
        if not dt:
            return None
        return int(dt.timestamp())

    def get_averageRating(self, obj):
        # Заглушка: пока рейтинги не реализованы, возвращаем 0.0
        # Можно заменить на агрегацию связанной модели Review.
        return 0.0

    def get_reviewsCount(self, obj):
        # Заглушка: пока отзывов нет в модели, возвращаем 0
        return 0


class ModeratorRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

