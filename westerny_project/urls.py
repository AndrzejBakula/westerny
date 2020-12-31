"""westerny_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from westerny_app.views import IndexView, MoviesView, AddMovieView, GenresView, AddGenreView, PeopleView
from westerny_app.views import AddPersonView, GenreDetailsView, EditGenreView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name="index"),
    path('movies/', MoviesView.as_view(), name="movies"),
    path('add_movie/', AddMovieView.as_view(), name="add-movie"),
    path('genres/', GenresView.as_view(), name="genres"),
    path('add_genre/', AddGenreView.as_view(), name="add-genre"),
    path('genre_details/<int:id>', GenreDetailsView.as_view(), name="genre-details"),
    path('edit_genre/<int:id>', EditGenreView.as_view(), name="edit-genre"),
    path('people/', PeopleView.as_view(), name="people"),
    path('add_person/', AddPersonView.as_view(), name="add-person")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
