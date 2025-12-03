from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Prefetch

from movies.models import Movie, Post
from movies.serializers.movie_detail import MovieDetailSerializer
from movies.serializers.movie_detail import ReviewSerializer
from movies.pagination import ReviewsPagination
from rest_framework import generics


class MovieDetailView(APIView):
    def get(self, request, pk):
        # Prefetch posts and user to avoid N+1 when serializing recent reviews
        posts_qs = Post.objects.filter(deleted=False).select_related('user')
        movie = get_object_or_404(
            Movie.objects.prefetch_related(
                Prefetch('posts', queryset=posts_qs),
            ),
            pk=pk
        )

        serializer = MovieDetailSerializer(movie, context={'request': request})
        return Response(serializer.data)


class MovieReviewsView(generics.ListAPIView):
    """Paginated top-level reviews for a movie. Returns immediate replies (limited) inside each review."""
    serializer_class = ReviewSerializer
    pagination_class = ReviewsPagination

    def get_queryset(self):
        movie_pk = self.kwargs.get('pk')
        qs = Post.objects.filter(movie_id=movie_pk, deleted=False)
        qs = qs.select_related('user')
        return qs.order_by('-creation_date')
