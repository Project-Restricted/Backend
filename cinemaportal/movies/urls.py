from django.urls import path
from .views.movie_views import MovieListView
from .views.movie_detail import MovieDetailView
from .views.movie_detail import MovieReviewsView
from .views.post_views import PostLikeToggleView, CreateReviewView
from .views.movie_views import CreateMovieView, UpdateMovieView

urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),
    path('create/', CreateMovieView.as_view(), name='movie-create'),
    path('<int:pk>/edit/', UpdateMovieView.as_view(), name='movie-edit'),
    path('<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('<int:pk>/reviews/', MovieReviewsView.as_view(), name='movie-reviews'),
    # create review
    path('posts/create/', CreateReviewView.as_view(), name='create-review'),
    # like/unlike post
    path('posts/<int:pk>/like/', PostLikeToggleView.as_view(), name='post-like'),
]
