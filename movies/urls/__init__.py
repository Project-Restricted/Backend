from django.urls import include, path

urlpatterns = [
    path('movies/', include('movies.urls.movie_urls')),
]