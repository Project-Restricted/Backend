from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from movies.models import Movie
from movies.serializers.movie_detail import MovieDetailSerializer

class MovieDetailView(APIView):
    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)
