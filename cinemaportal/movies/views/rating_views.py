from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP

from movies.models import Movie, MovieRating
from movies.serializers.movie_rating import MovieRatingSerializer


class RateMovieView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            movie = get_object_or_404(Movie, pk=pk)
            serializer = MovieRatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            score = serializer.validated_data['score']

            # create or update user's rating
            obj, created = MovieRating.objects.update_or_create(
                movie=movie, user=request.user, defaults={'score': score}
            )

            # compute new average and store on movie (one decimal place)
            avg = MovieRating.objects.filter(movie=movie).aggregate(avg=Avg('score'))['avg'] or 0
            # use Decimal(str(...)) to avoid float->Decimal issues
            avg_decimal = (Decimal(str(avg)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            movie.rating = avg_decimal
            movie.save(update_fields=['rating'])

            return Response({'movie': movie.pk, 'rating': float(avg_decimal)}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log server-side exception and return JSON (avoid HTML 500)
            import logging
            logging.exception('Error while rating movie %s', pk)
            return Response(
                {
                    'success': False,
                    'error': 'Internal Server Error',
                    'details': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
