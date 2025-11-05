from rest_framework import generics
from movies.models.movie import Movie
from movies.serializers.movie_serializer import MovieDetailSerializer

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.filter(approved=True)
    serializer_class = MovieDetailSerializer
