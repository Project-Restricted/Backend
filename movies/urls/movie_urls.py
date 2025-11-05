from django.urls import path
from movies.views.movie_views import MovieDetailView

urlpatterns = [
    path('<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
]