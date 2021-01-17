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
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from westerny_app.views import IndexView, MoviesView, AddMovieView, GenresView, AddGenreView, PeopleView
from westerny_app.views import AddPersonView, GenreDetailsView, EditGenreView, DeleteGenreView
from westerny_app.views import RegisterView, LoginView, LogoutView, RulesView, MyPlaceView, SearchMovieView
from westerny_app.views import SearchPersonView, StatsView, VerificationView, WaitingGenresView
from westerny_app.views import AcceptGenreView, AddArticleGenreView, DeleteArticleGenreView
from westerny_app.views import WaitingPeopleView, PersonDetailsView, EditPersonView, AcceptPersonView
from westerny_app.views import AddArticlePersonView, DeleteArticlePersonView, DeletePersonView, WaitingMoviesView
from westerny_app.views import MovieDetailsView, DeleteMovieView, AcceptMovieView, AddArticleMovieView
from westerny_app.views import EditMovieView, DeleteArticleMovieView, AddActorMovieView, DeleteActorMovieView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name="index"),
    path('rules/', RulesView.as_view(), name="rules"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my_place/', MyPlaceView.as_view(), name='my-place'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('movies/', MoviesView.as_view(), name="movies"),
    path('search_movie/', SearchMovieView.as_view(), name="search-movie"),
    path('add_movie/', AddMovieView.as_view(), name="add-movie"),
    path('movie_details/<int:id>', MovieDetailsView.as_view(), name="movie-details"),
    path('edit_movie/<int:id>', EditMovieView.as_view(), name="edit-movie"),
    path('delete_movie/<int:id>', DeleteMovieView.as_view(), name="delete-movie"),
    path('accept_movie/<int:id>', AcceptMovieView.as_view(), name="accept-movie"),
    path('waiting_movies/', WaitingMoviesView.as_view(), name="waiting-movies"),
    path('add_actor_movie/<int:id>', AddActorMovieView.as_view(), name="add-actor-movie"),
    path('delete_actor_movie/<int:movie_id>/<int:person_id>', DeleteActorMovieView.as_view(), name="delete-actor-movie"),
    path('genres/', GenresView.as_view(), name="genres"),
    path('add_genre/', AddGenreView.as_view(), name="add-genre"),
    path('genre_details/<int:id>', GenreDetailsView.as_view(), name="genre-details"),
    path('edit_genre/<int:id>', EditGenreView.as_view(), name="edit-genre"),
    path('delete_genre/<int:id>', DeleteGenreView.as_view(), name="delete-genre"),
    path('waiting_genres/', WaitingGenresView.as_view(), name="waiting-genres"),
    path('accept_genre/<int:id>', AcceptGenreView.as_view(), name="accept-genre"),
    path('people/', PeopleView.as_view(), name="people"),
    path('add_person/', AddPersonView.as_view(), name="add-person"),
    path('person_details/<int:id>', PersonDetailsView.as_view(), name="person-details"),
    path('edit_person/<int:id>', EditPersonView.as_view(), name="edit-person"),
    path('delete_person/<int:id>', DeletePersonView.as_view(), name="delete-person"),
    path('waiting_people/', WaitingPeopleView.as_view(), name="waiting-people"),
    path('accept_person/<int:id>', AcceptPersonView.as_view(), name="accept-person"),
    path('search_person/', SearchPersonView.as_view(), name="search-person"),
    path('add_article_genre/<int:id>', AddArticleGenreView.as_view(), name="add-article-genre"),
    path('delete_article_genre/<int:genre_id>/<int:article_id>', DeleteArticleGenreView.as_view(), name="delete-article-genre"),
    path('add_article_person/<int:id>', AddArticlePersonView.as_view(), name="add-article-person"),
    path('delete_article_person/<int:person_id>/<int:article_id>', DeleteArticlePersonView.as_view(), name="delete-article-person"),
    path('add_article_movie/<int:id>', AddArticleMovieView.as_view(), name="add-article-movie"),
    path('delete_article_movie/<int:movie_id>/<int:article_id>', DeleteArticleMovieView.as_view(), name="delete-article-movie"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
