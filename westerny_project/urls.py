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
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url, include
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
from westerny_app.views import UserDetailsView, GivePromotionView, PromotionAsksView
from westerny_app.views import RequestPasswordResetEmail, CompletePasswordReset, AcceptArticlePersonView, AcceptArticleMovieView
from westerny_app.views import GiveEditPersonView, GiveEditMovieView, MyMoviesView, SearchMyMovieView, MyPeopleView
from westerny_app.views import SearchMyPersonView, MyGenresView, PeopleRankView, MoviesRankView
from westerny_app.views import AddWatchlistView, RemoveWatchlistView, WatchlistView, RatedMoviesView, RatedPeopleView
from westerny_app.views import MoviesNewestView, PeopleNewestView, AddedMoviesView, AddedPeopleView, AddedGenresView
from westerny_app.views import SoldiersView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name="index"),
    path('rules/', RulesView.as_view(), name="rules"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my_place/', MyPlaceView.as_view(), name='my-place'),
    path('my_movies/', MyMoviesView.as_view(), name='my-movies'),
    path('my_people/', MyPeopleView.as_view(), name='my-people'),
    path('my_genres/', MyGenresView.as_view(), name='my-genres'),
    path('rated_movies/', RatedMoviesView.as_view(), name='rated-movies'),
    path('rated_people/', RatedPeopleView.as_view(), name='rated-people'),
    path('user_details/<int:user_id>', UserDetailsView.as_view(), name="user-details"),
    path('added_movies/<int:soldier_id>', AddedMoviesView.as_view(), name="added-movies"),
    path('added_people/<int:soldier_id>', AddedPeopleView.as_view(), name="added-people"),
    path('added_genres/<int:soldier_id>', AddedGenresView.as_view(), name="added-genres"),
    path('give_promotion/<int:soldier_id>', GivePromotionView.as_view(), name="give-promotion"),
    path('promotion_asks/', PromotionAsksView.as_view(), name="promotion-asks"),
    path('stats/', StatsView.as_view(), name='stats'),
    path('movies/', MoviesView.as_view(), name="movies"),
    path('movies_newest/', MoviesNewestView.as_view(), name="movies-newest"),
    path('search_movie/', SearchMovieView.as_view(), name="search-movie"),
    path('search_my_movie/', SearchMyMovieView.as_view(), name="search-my-movie"),
    path('movies_rank/', MoviesRankView.as_view(), name="movies-rank"),
    path('add_movie/', AddMovieView.as_view(), name="add-movie"),
    path('movie_details/<int:movie_id>', MovieDetailsView.as_view(), name="movie-details"),
    path('edit_movie/<int:movie_id>', EditMovieView.as_view(), name="edit-movie"),
    path('delete_movie/<int:movie_id>', DeleteMovieView.as_view(), name="delete-movie"),
    path('accept_movie/<int:movie_id>', AcceptMovieView.as_view(), name="accept-movie"),
    path('waiting_movies/', WaitingMoviesView.as_view(), name="waiting-movies"),
    path('add_actor_movie/<int:movie_id>', AddActorMovieView.as_view(), name="add-actor-movie"),
    path('delete_actor_movie/<int:movie_id>/<int:person_id>', DeleteActorMovieView.as_view(), name="delete-actor-movie"),
    path('gitve_edit_movie/<int:movie_id>/<int:soldier_id>', GiveEditMovieView.as_view(), name="give-edit-movie"),
    path('genres/', GenresView.as_view(), name="genres"),
    path('add_genre/', AddGenreView.as_view(), name="add-genre"),
    path('genre_details/<int:genre_id>', GenreDetailsView.as_view(), name="genre-details"),
    path('edit_genre/<int:genre_id>', EditGenreView.as_view(), name="edit-genre"),
    path('delete_genre/<int:genre_id>', DeleteGenreView.as_view(), name="delete-genre"),
    path('waiting_genres/', WaitingGenresView.as_view(), name="waiting-genres"),
    path('accept_genre/<int:genre_id>', AcceptGenreView.as_view(), name="accept-genre"),
    path('people/', PeopleView.as_view(), name="people"),
    path('people_newest/', PeopleNewestView.as_view(), name="people-newest"),
    path('add_person/', AddPersonView.as_view(), name="add-person"),
    path('person_details/<int:person_id>', PersonDetailsView.as_view(), name="person-details"),
    path('edit_person/<int:person_id>', EditPersonView.as_view(), name="edit-person"),
    path('delete_person/<int:person_id>', DeletePersonView.as_view(), name="delete-person"),
    path('waiting_people/', WaitingPeopleView.as_view(), name="waiting-people"),
    path('accept_person/<int:person_id>', AcceptPersonView.as_view(), name="accept-person"),
    path('search_person/', SearchPersonView.as_view(), name="search-person"),
    path('search_my_person/', SearchMyPersonView.as_view(), name="search-my-person"),
    path('people_rank/', PeopleRankView.as_view(), name="people-rank"),
    path('give_edit_person/<int:person_id>/<int:soldier_id>', GiveEditPersonView.as_view(), name="give-edit-person"),
    path('add_article_genre/<int:id>', AddArticleGenreView.as_view(), name="add-article-genre"),
    path('delete_article_genre/<int:genre_id>/<int:article_id>', DeleteArticleGenreView.as_view(), name="delete-article-genre"),
    path('add_article_person/<int:id>', AddArticlePersonView.as_view(), name="add-article-person"),
    path('delete_article_person/<int:person_id>/<int:article_id>', DeleteArticlePersonView.as_view(), name="delete-article-person"),
    path('accept_article_person/<int:person_id>/<int:article_id>', AcceptArticlePersonView.as_view(), name="accept-article-person"),
    path('add_article_movie/<int:id>', AddArticleMovieView.as_view(), name="add-article-movie"),
    path('delete_article_movie/<int:movie_id>/<int:article_id>', DeleteArticleMovieView.as_view(), name="delete-article-movie"),
    path('accept_article_movie/<int:movie_id>/<int:article_id>', AcceptArticleMovieView.as_view(), name="accept-article-movie"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
    path('add_watchlist/<int:movie_id>', AddWatchlistView.as_view(), name="add-watchlist"),
    path('add_removelist/<int:movie_id>', RemoveWatchlistView.as_view(), name="remove-watchlist"),
    path('watchlist/', WatchlistView.as_view(), name="watchlist"),
    path('soldiers/', SoldiersView.as_view(), name="soldiers"),

    path('reset_password/', RequestPasswordResetEmail.as_view(), name='reset-password'),
    path('set_new_password/<uidb64>/<token>', CompletePasswordReset.as_view(), name="set-new-password"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
