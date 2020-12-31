from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datetime import timezone, date, timedelta
from django.views import View
from westerny_app.models import Movie, Genre, Person
from westerny_app.forms import AddMovieForm, AddGenreForm, AddPersonForm, EditGenreForm


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
    
    def post(self, request):
        form = AddGenreForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            genres = [i.name.title() for i in Genre.objects.all()]
            genre = data["name"].title()
            if genre in genres:
                ctx = {
                    "error_message": "Ten gatunek już jest w bazie.",
                    "form": form,
                    "data": request.POST
                }
                return render(request, "add_genre.html", ctx)
            else:
                Genre.objects.create(
                    name=genre,
                    genre_image=request.FILES.get("image"),
                    who_added="Westerny" #PILNIE DO POPRAWY O USERA
                )
                return redirect("/genres")


class GenreDetailsView(View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        return render(request, "genre_details.html", {"genre": genre})


class EditGenreView(View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        initial_data = {
            "name": genre.name
        }
        form = EditGenreForm(initial=initial_data)
        ctx = {
            "genre": genre,
            "form": form
        }
        return render(request, "edit_genre.html", ctx)
    
    def post(self, request, id):
        genre = Genre.objects.get(id=id)
        genre.name = request.POST.get("name")
        genre.who_added = "Westerny" #PILNIE TO POPRAWIĆ
        if request.FILES.get("image") != None or request.POST.get("delete_image"):
            genre.genre_image = request.FILES.get("image")
        genre.save()
        initial_data = {
            "name": genre.name
        }
        form = EditGenreForm(initial=initial_data)
        ctx = {
            "genre": genre,
            "form": form
        }
        return render(request, "edit_genre.html", {"genre": genre})



class DeleteGenreView(View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        return render(request, "delete_genre.html", {"genre": genre})
    
    def post(self, request, id):
        genre = Genre.objects.get(id=id)
        genre.delete()
        return redirect("/genres")


class PeopleView(View):
    def get(self, request):
        people = Person.objects.all().order_by("last_name")
        return render(request, "people.html", {"people": people})


class AddPersonView(View):
    def get(self, request):
        form = AddPersonForm()
        return render(request, "add_person.html", {"form": form})