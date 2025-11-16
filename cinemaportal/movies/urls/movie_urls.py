# movies/urls/movie_urls.py
from django.urls import path
from movies.views.movie_views import MovieListView

urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),  # доступно: /api/v1/movies/
]