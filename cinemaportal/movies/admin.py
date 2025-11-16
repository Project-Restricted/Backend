from django.contrib import admin

# Register your models here.
from django.contrib import admin
from movies.models.movie import Movie
from movies.models.movie import MovieSource
from movies.models.movie_tag import MovieTag
from movies.models.country import Country
from movies.models.genre import Genre
from movies.models.genre import MovieGenre
from movies.models.actor import Actor
from movies.models.actor import MovieActor
from movies.models.director import Director
from movies.models.director import MovieDirector
from movies.models.tag import Tag
from movies.models.post import Post

admin.site.register(Movie)
admin.site.register(MovieSource)
admin.site.register(MovieTag)
admin.site.register(Country)
admin.site.register(Genre)
admin.site.register(MovieGenre)
admin.site.register(Actor)
admin.site.register(MovieActor)
admin.site.register(Director)
admin.site.register(MovieDirector)
admin.site.register(Tag)
admin.site.register(Post)