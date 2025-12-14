from django.db.models import Q
from rest_framework import generics
from movies.models.movie import Movie
from movies.serializers.movie_serializer import MovieListSerializer
from movies.pagination import InfiniteScrollPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from movies.serializers.movie_detail import CreateMovieSerializer, MovieDetailSerializer
from movies.serializers.movie_detail import UpdateMovieSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class MovieListView(generics.ListAPIView):
    """
    GET /api/v1/movies/?page=1&search=...&genre=1,2&tags=cyberpunk,-drama&year=2022&country=USA
    Возвращает упрощённые превью фильмов (FilmPreview).
    """
    serializer_class = MovieListSerializer
    pagination_class = InfiniteScrollPagination

    def get_queryset(self):
        qs = Movie.objects.filter(approved=True)

        qs = qs.select_related('country') \
               .prefetch_related('genres', 'actors', 'tags')

        params = self.request.query_params

        search = params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(tags__tag__icontains=search) |
                Q(actors__firstname__icontains=search) |
                Q(actors__lastname__icontains=search)
            ).distinct()

        genre_params = params.getlist('genre') 
        if not genre_params:
            raw = params.get('genre')
            if raw:
                genre_params = [g.strip() for g in raw.split(',') if g.strip()]

        if genre_params:
            try:
                genre_ids = [int(g) for g in genre_params]
                for gid in genre_ids:
                    qs = qs.filter(genres__id=gid)
                qs = qs.distinct()
            except ValueError:
                pass

        raw_tags = params.get('tags')
        if raw_tags:
            tokens = [t.strip() for t in raw_tags.split(',') if t.strip()]
            include = [t for t in tokens if not t.startswith('-')]
            exclude = [t[1:] for t in tokens if t.startswith('-')]

            for t in include:
                qs = qs.filter(tags__tag__iexact=t)
            for t in exclude:
                qs = qs.exclude(tags__tag__iexact=t)
            qs = qs.distinct()

        year = params.get('year')
        if year:
            try:
                year_int = int(year)
                qs = qs.filter(year=year_int)
            except ValueError:
                pass

        country = params.get('country')
        if country:
            if country.isdigit():
                qs = qs.filter(country__id=int(country))
            else:
                qs = qs.filter(country__name__iexact=country)

        ordering = params.get('ordering')
        if ordering:
            allowed = {'rating', '-rating', 'year', '-year', 'id', '-id'}
            if ordering in allowed:
                qs = qs.order_by(ordering)

        return qs


class CreateMovieView(generics.CreateAPIView):
    """Allow moderators to create movies with poster upload, actors, directors."""
    serializer_class = CreateMovieSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, 'role', None) != 'moderator':
            return Response({'success': False, 'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        movie = serializer.save()
        # return full movie detail
        return Response({'success': True, 'movie': MovieDetailSerializer(movie, context={'request': request}).data}, status=status.HTTP_201_CREATED)


class UpdateMovieView(APIView):
    """Allow moderators to partially update an existing movie."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        if getattr(user, 'role', None) != 'moderator':
            return Response({'success': False, 'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        from movies.models.movie import Movie
        movie = get_object_or_404(Movie, pk=pk)

        serializer = UpdateMovieSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        movie = serializer.update(movie, serializer.validated_data)

        return Response({'success': True, 'movie': MovieDetailSerializer(movie, context={'request': request}).data}, status=status.HTTP_200_OK)
