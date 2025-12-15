from rest_framework import serializers
from django.conf import settings

from movies.models import Movie, Post
from users.models import User


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


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("movie", "text")

    def create(self, validated_data):
        request = self.context["request"]

        return Post.objects.create(
            user=request.user,   # ← ВАЖНО
            movie=validated_data["movie"],
            text=validated_data["text"],
        )


class MovieDetailSerializer(serializers.ModelSerializer):
    posterUrl = serializers.SerializerMethodField()
    videoUrl = serializers.SerializerMethodField()

    genres = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()

    duration = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    # Present country as a name string (frontend expects a string), and rating as numeric
    country = serializers.SerializerMethodField()
    rating = serializers.FloatField()
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

    def get_country(self, obj):
        if obj.country:
            return obj.country.name
        return None


    def get_posterUrl(self, obj):
        if not obj.poster_url:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(obj.poster_url)


    def get_videoUrl(self, obj):
        return obj.video_url


    def get_genres(self, obj):
        return [g.name for g in obj.genres.all()]


    def get_tags(self, obj):
        return [t.tag for t in obj.tags.all()]

    # actors formatted (uses Actor.__str__())
    def get_actors(self, obj):
        return [str(a) for a in obj.actors.all()]   # __str__ в модели актёра

    # director (comma-separated if multiple)
    def get_director(self, obj):
        directors = obj.directors.all()
        if not directors:
            return None
        return ", ".join(str(d) for d in directors)

    # duration in minutes
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


# Serializer for creating movies (moderator-only)
class CreateMovieSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    video_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    # duration in minutes
    duration = serializers.IntegerField(required=False, allow_null=True)
    # poster file upload
    poster = serializers.ImageField(required=False, allow_null=True, write_only=True)

    # actors/directors: list of ids or names ("First Last")
    actors = serializers.ListField(child=serializers.CharField(), required=False)
    directors = serializers.ListField(child=serializers.CharField(), required=False)

    # country: accept id or name
    country = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # minimal validation
        if not data.get('title'):
            raise serializers.ValidationError('title is required')
        return data

    def create(self, validated_data):
        from movies.models.movie import Movie
        from movies.models.actor import Actor
        from movies.models.director import Director
        from movies.models.country import Country
        from django.conf import settings
        import os
        import uuid
        from datetime import timedelta

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # handle poster file
        poster_file = validated_data.pop('poster', None)
        poster_url = None
        if poster_file:
            posters_dir = os.path.join(settings.MEDIA_ROOT, 'posters')
            os.makedirs(posters_dir, exist_ok=True)
            ext = os.path.splitext(poster_file.name)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            dest_path = os.path.join(posters_dir, filename)
            with open(dest_path, 'wb+') as dst:
                for chunk in poster_file.chunks():
                    dst.write(chunk)
            poster_url = settings.MEDIA_URL.rstrip('/') + f"/posters/{filename}"


        dur_minutes = validated_data.pop('duration', None)
        duration_td = None
        if dur_minutes is not None:
            try:
                duration_td = timedelta(minutes=int(dur_minutes))
            except Exception:
                duration_td = None

        country_val = validated_data.pop('country', None)
        country_obj = None
        if country_val:
            # try id then name
            try:
                cid = int(country_val)
                country_obj = Country.objects.filter(pk=cid).first()
            except Exception:
                country_obj = Country.objects.filter(name__iexact=country_val).first()

        movie = Movie.objects.create(
            title=validated_data.get('title'),
            description=validated_data.get('description', ''),
            year=validated_data.get('year'),
            video_url=validated_data.get('video_url', None),
            duration=duration_td,
            poster_url=poster_url,
            country=country_obj,
            created_by=user,
            approved=True,
        )

        # attach actors
        actors_list = validated_data.get('actors') or []
        for a in actors_list:
            # if looks like id
            actor_obj = None
            try:
                aid = int(a)
                actor_obj = Actor.objects.filter(pk=aid).first()
            except Exception:
                # parse name
                parts = a.split()
                firstname = parts[0]
                lastname = ' '.join(parts[1:]) if len(parts) > 1 else ''
                actor_obj, _ = Actor.objects.get_or_create(firstname=firstname, lastname=lastname)
            if actor_obj:
                movie.actors.add(actor_obj)

        # attach directors
        directors_list = validated_data.get('directors') or []
        for d in directors_list:
            director_obj = None
            try:
                did = int(d)
                director_obj = Director.objects.filter(pk=did).first()
            except Exception:
                parts = d.split()
                firstname = parts[0]
                lastname = ' '.join(parts[1:]) if len(parts) > 1 else ''
                director_obj, _ = Director.objects.get_or_create(firstname=firstname, lastname=lastname)
            if director_obj:
                movie.directors.add(director_obj)

        return movie


class UpdateMovieSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    video_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    # duration in minutes
    duration = serializers.IntegerField(required=False, allow_null=True)
    # poster file upload (replace existing)
    poster = serializers.ImageField(required=False, allow_null=True, write_only=True)

    # actors/directors: list of ids or names ("First Last")
    actors = serializers.ListField(child=serializers.CharField(), required=False)
    directors = serializers.ListField(child=serializers.CharField(), required=False)

    # country: accept id or name
    country = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        from movies.models.actor import Actor
        from movies.models.director import Director
        from movies.models.country import Country
        from django.conf import settings
        import os
        from datetime import timedelta

        # poster handling (optional replacement)
        poster_file = validated_data.pop('poster', None)
        if poster_file:
            posters_dir = os.path.join(settings.MEDIA_ROOT, 'posters')
            os.makedirs(posters_dir, exist_ok=True)
            ext = os.path.splitext(poster_file.name)[1]
            import uuid
            filename = f"{uuid.uuid4().hex}{ext}"
            dest_path = os.path.join(posters_dir, filename)
            with open(dest_path, 'wb+') as dst:
                for chunk in poster_file.chunks():
                    dst.write(chunk)
            instance.poster_url = settings.MEDIA_URL.rstrip('/') + f"/posters/{filename}"

        # duration (minutes) -> timedelta
        if 'duration' in validated_data:
            dur_minutes = validated_data.pop('duration')
            if dur_minutes is None:
                instance.duration = None
            else:
                try:
                    instance.duration = timedelta(minutes=int(dur_minutes))
                except Exception:
                    pass

        # country
        if 'country' in validated_data:
            country_val = validated_data.pop('country')
            country_obj = None
            if country_val:
                try:
                    cid = int(country_val)
                    country_obj = Country.objects.filter(pk=cid).first()
                except Exception:
                    country_obj = Country.objects.filter(name__iexact=country_val).first()
            instance.country = country_obj

        # basic scalar fields
        for attr in ('title', 'description', 'year', 'video_url'):
            if attr in validated_data:
                setattr(instance, attr, validated_data.get(attr))

        instance.save()

        # replace actors if provided
        if 'actors' in validated_data:
            instance.actors.clear()
            actors_list = validated_data.get('actors') or []
            for a in actors_list:
                actor_obj = None
                try:
                    aid = int(a)
                    actor_obj = Actor.objects.filter(pk=aid).first()
                except Exception:
                    parts = a.split()
                    firstname = parts[0]
                    lastname = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    actor_obj, _ = Actor.objects.get_or_create(firstname=firstname, lastname=lastname)
                if actor_obj:
                    instance.actors.add(actor_obj)

        # replace directors if provided
        if 'directors' in validated_data:
            instance.directors.clear()
            directors_list = validated_data.get('directors') or []
            for d in directors_list:
                director_obj = None
                try:
                    did = int(d)
                    director_obj = Director.objects.filter(pk=did).first()
                except Exception:
                    parts = d.split()
                    firstname = parts[0]
                    lastname = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    director_obj, _ = Director.objects.get_or_create(firstname=firstname, lastname=lastname)
                if director_obj:
                    instance.directors.add(director_obj)

        return instance
