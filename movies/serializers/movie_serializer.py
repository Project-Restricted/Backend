from rest_framework import serializers
from movies.models.movie import Movie
from movies.models.actor import Actor
from movies.models.genre import Genre
from movies.models.tag import Tag

class ActorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class MovieDetailSerializer(serializers.ModelSerializer):
    actors = ActorShortSerializer(many=True)
    genres = GenreSerializer(many=True)
    tags = TagSerializer(many=True)
    country = serializers.StringRelatedField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'year', 'poster_url',
            'video_url', 'duration', 'country', 'rating',
            'actors', 'genres', 'tags'
        ]
