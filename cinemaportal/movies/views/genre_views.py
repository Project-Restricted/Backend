from rest_framework import generics
from movies.models.genre import Genre
from movies.serializers.genre_serializer import GenreSerializer


class GenreListView(generics.ListAPIView):
    """Read-only list of genres used by frontend for filtering."""
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    # Return a plain list (frontend expects an array of objects)
    pagination_class = None
