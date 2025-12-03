from django.urls import path
from .views.movie_views import MovieListView
from .views.movie_detail import MovieDetailView

urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),
    path('<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
]
