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
from westerny_app.views import AcceptGenreView

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
    path('genres/', GenresView.as_view(), name="genres"),
    path('add_genre/', AddGenreView.as_view(), name="add-genre"),
    path('genre_details/<int:id>', GenreDetailsView.as_view(), name="genre-details"),
    path('edit_genre/<int:id>', EditGenreView.as_view(), name="edit-genre"),
    path('delete_genre/<int:id>', DeleteGenreView.as_view(), name="delete-genre"),
    path('waiting_genres/', WaitingGenresView.as_view(), name="waiting-genres"),
    path('accept_genre/<int:id>', AcceptGenreView.as_view(), name="accept-genre"),
    path('people/', PeopleView.as_view(), name="people"),
    path('search_person/', SearchPersonView.as_view(), name="search-person"),
    path('add_person/', AddPersonView.as_view(), name="add-person"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
