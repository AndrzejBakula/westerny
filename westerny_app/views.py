from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import timezone, date, timedelta
from django.views import View
from westerny_app.models import Movie
from westerny_app.forms import AddMovieForm


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