from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import timezone, date, timedelta
from django.views import View
from westerny_app.models import Movie, Genre, Person
from westerny_app.forms import AddMovieForm, AddGenreForm


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


class MoviesView(View):
    def get(self, request):
        movies = Movie.objects.all().order_by("year")
        return render(request, "movies.html", {"movies": movies})


class AddMovieView(View):
    def get(self, request):
        form = AddMovieForm()
        return render(request, "add_movie.html", {"form": form})


class GenresView(View):
    def get(self, request):
        genres = Genre.objects.all().order_by("name")
        return render(request, "genres.html", {"genres": genres})


class AddGenreView(View):
    def get(self, request):
        form = AddGenreForm()
        return render(request, "add_genre.html", {"form": form})


class PeopleView(View):
    def get(self, request):
        people = Person.objects.all().order_by("last_name")
        return render(request, "people.html", {"people": people})