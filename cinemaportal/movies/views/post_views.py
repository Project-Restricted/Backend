from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from movies.models import Post
from movies.serializers.movie_detail import ReviewSerializer, CreateReviewSerializer
from movies.pagination import ReviewsPagination


class CreateReviewView(generics.CreateAPIView):
    """Создание нового отзыва на фильм."""
    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # вернуть полный объект отзыва (ReviewSerializer), а не CreateReviewSerializer
        post = Post.objects.get(pk=response.data['id'])
        return Response(
            ReviewSerializer(post, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, deleted=False)
        user = request.user

        if post.liked_by.filter(pk=user.pk).exists():
            post.liked_by.remove(user)
            liked = False
        else:
            post.liked_by.add(user)
            liked = True

        # return updated counts
        data = {
            'id': post.pk,
            'likes': post.likes,
            'likedByCurrentUser': liked
        }
        return Response(data, status=status.HTTP_200_OK)


