from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from datetime import timezone, date, timedelta
from .utils import token_generator
from django.views import View
from django.contrib.auth.models import User
from westerny_project.settings import PROTOCOLE
from westerny_app.models import Movie, Genre, Person, Article, Rank, UserRank, PersonRating, Rating
from westerny_app.forms import AddMovieForm, AddGenreForm, AddPersonForm, EditGenreForm, RegisterForm, LoginForm
from westerny_app.forms import SearchMovieForm, SearchPersonForm, AddArticleForm, EditPersonForm, RatingForm


#RANK CHECKING METHOD:
def check_rank(user):
    userrank = UserRank.objects.get(user=user.id)

    kawalerzysta = Rank.objects.get(name="kawalerzysta")
    kapral = Rank.objects.get(name="kapral")
    sierzant = Rank.objects.get(name="sierżant")
    porucznik = Rank.objects.get(name="porucznik")
    kapitan = Rank.objects.get(name="kapitan")
    major = Rank.objects.get(name="major")
    pulkownik = Rank.objects.get(name="pułkownik")
    general = Rank.objects.get(name="generał")
    gubernator = Rank.objects.get(name="gubernator")

    movies = Movie.objects.filter(movie_added_by=user.id)
    added_movies = len([i for i in movies if i.movie_accepted_by])*2
    people = Person.objects.filter(person_added_by=user.id)
    added_people = len([i for i in people if i.person_accepted_by])
    genres = Genre.objects.filter(genre_added_by=user.id)
    added_genre = len([i for i in genres if i.genre_accepted_by])*2
    sum_of_added = added_genre+added_movies+added_people

    accpted_movies = len(Movie.objects.filter(movie_accepted_by=user.id))
    accepted_people = len(Person.objects.filter(person_accepted_by=user.id))
    accepted_genre = len(Genre.objects.filter(genre_accepted_by=user.id))
    sum_of_accepted = accepted_genre+accepted_people+accpted_movies

    if user.username == "Westerny":
        userrank.rank = gubernator
        return userrank.save()
    elif user.is_staff == False:
        userrank.rank = kawalerzysta
        if 10 <= sum_of_added < 30:
            userrank.rank = kapral
            return userrank.save()
        elif sum_of_added >= 30:
            userrank.rank = sierzant
            return userrank.save()
        return userrank.save()
    elif user.is_staff == True:
        userrank.rank = porucznik
        if (30 <= sum_of_added < 50) or ( 10 <= sum_of_accepted < 30):
            userrank.rank = kapitan
            return userrank.save()
        elif (50 <= sum_of_added < 75) or (30 <= sum_of_accepted < 50):
            userrank.rank = major
            return userrank.save()
        elif (75 <= sum_of_added < 100) or (50 <= sum_of_accepted < 75):
            userrank.rank = pulkownik
            return userrank.save()
        return userrank.save()
    elif user.is_superuser == True:
        userrank.rank = general
        return userrank.save()       


#USER CHECK CLASSES:
class VerificationView(View):
    def get(self, request, uidb64, token):
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user.is_active = True
        user.save()
        return redirect("login")


class SuperUserCheck(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser


class StaffMemberCheck(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff


class ActivateUserCheck(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated


#MAIN VIEWS CLASSES:
class IndexView(View):
    def get(self, request):
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
            check_rank(user)
        return render(request, "index.html")


class RulesView(View):
    def get(self, request):
        return render(request, "rules.html")


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})
    
    def post(self, request):
        users = [i.username for i in User.objects.all()]
        # emails = [i.email for i in User.objeects.all()]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        message = ""
        initial_data = {
            "username": username,
            "email": email,
        }
        form = RegisterForm(initial=initial_data)
        if password != password2:
            message = "Proszę podać dwa takie same hasła."
            ctx = {
                "username": username,
                "email": email,
                "message": message,
                "form": form
            }
            return render(request, "register.html", ctx)
        elif len(password) < 6:
            message = "Hasło powinno mieć przynajmniej 6 znaków."
            ctx = {
                "username": username,
                "email": email,
                "message": message,
                "form": form
            }
            return render(request, "register.html", ctx)
        elif username in ("", None) or email in ("", None) or password in ("", None):
            message = "Proszę wypełnić wszystkie pola."
            ctx = {
                "username": username,
                "email": email,
                "message": message,
                "form": form
            }
            return render(request, "register.html", ctx)
        elif username in users:
            message = "Taki kawalerzysta widnieje już w rejestrze pułku."
            ctx = {
                "email": email,
                "message": message,
                "form": form
            }
            return render(request, "register.html", ctx)
        else:
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.is_active = False
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse("activate", kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})

            activate_url = PROTOCOLE+domain+link

            email_subject = "Aktywuj konto kawalerzysty."
            email_body = "Baczność, rekrucie " + user.username + "! Użyj poniższego linku werbunkowego i udaj się do kwatermistrza.\n" + activate_url
            email = EmailMessage(
                email_subject,
                email_body,
                "noreply@semycolon.com",
                [user.email],
                )
            
            email.send(fail_silently=False)
            rank = Rank.objects.get(name="kawalerzysta")
            UserRank.objects.create(user=user, rank=rank)
            message = f"Dodano nowego kawalerzystę {user.username}. Wysłano telegram potwierdzający do skrzynki na listy."
            form = LoginForm()
            ctx = {
                "message": message,
                "form": form
            }
            return render(request, "login.html", ctx)


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session["logged"] = True
            request.session["user_id"] = user.pk
            return redirect("/")
        return redirect("/register")


class LogoutView(ActivateUserCheck, View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            request.session["logged"] = False
        return redirect("/index")


class MyPlaceView(ActivateUserCheck, View):
    def get(self, request):
        user = User.objects.get(pk=request.session.get("user_id"))
        westerns = Movie.objects.filter(movie_added_by=user.id)
        added_westerns = len([i for i in westerns if i.movie_accepted_by])
        people = Person.objects.filter(person_added_by=user.id)
        added_people = len([i for i in people if i.person_accepted_by])
        genres = Genre.objects.filter(genre_added_by=user.id)
        added_genres = len([i for i in genres if i.genre_accepted_by])
        links = len(Article.objects.filter(article_added_by=user.id))
        notes = added_westerns + added_people + added_genres + links

        accepted_westerns = len(Movie.objects.filter(movie_accepted_by=user.id))
        accepted_people = len(Person.objects.filter(person_accepted_by=user.id))
        accepted_genres = len(Genre.objects.filter(genre_accepted_by=user.id))
        accepted_notes = accepted_westerns + accepted_people + accepted_genres

        ctx = {
            "westerns": added_westerns,
            "people": added_people,
            "genres": added_genres,
            "notes": notes,
            "links": links,
            "accepted_westerns": accepted_westerns,
            "accepted_people": accepted_people,
            "accepted_genres": accepted_genres,
            "accepted_notes": accepted_notes
        }
        return render(request, "my_place.html", ctx)


class StatsView(View):
    def get(self, request):
        users = len(User.objects.all())
        officers = len(User.objects.filter(is_staff=True))
        commanders = len(User.objects.filter(is_superuser=True))
        cavaliers = len(User.objects.filter(is_active=True, is_staff=False, is_superuser=False))
        civils = users - officers - commanders - cavaliers
        westerns = len(Movie.objects.all())
        people = len(Person.objects.all())
        genres = len(Genre.objects.all())
        notes = westerns + people + genres
        links = len(Article.objects.all())

        ctx = {
            "users": users,
            "officers": officers,
            "commanders": commanders,
            "cavaliers": cavaliers,
            "civils": civils,
            "westerns": westerns,
            "people": people,
            "genres": genres,
            "notes": notes,
            "links": links
        }
        return render(request, "stats.html", ctx)


class MoviesView(View):
    def get(self, request):
        movies = Movie.objects.all().order_by("year")
        return render(request, "movies.html", {"movies": movies})


class SearchMovieView(View):
    def get(self, request):
        form = SearchMovieForm()
        return render(request, "search_movie.html", {"form": form})

    def post(self, request):
        form = SearchMovieForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            movies = Movie.objects.filter(title__icontains=text).order_by(
                "title"
            )

            ctx = {
                "form": form,
                "movies": movies,
                "post": request.POST
                }
            return render(request, "search_movie.html", ctx)


class AddMovieView(ActivateUserCheck, View):
    def get(self, request):
        form = AddMovieForm()
        return render(request, "add_movie.html", {"form": form})


class GenresView(View):
    def get(self, request):
        genres = Genre.objects.all().order_by("name")
        waiting_genres = len([i for i in Genre.objects.all() if i.genre_accepted_by == None])
        ctx = {
            "genres": genres,
            "waiting_genres": waiting_genres
        }
        return render(request, "genres.html", ctx)


class AddGenreView(StaffMemberCheck, View):
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
                user = User.objects.get(pk=int(request.session.get("user_id")))
                if user.is_superuser == True:
                    genre = Genre.objects.create(
                        name=genre,
                        genre_description=request.POST.get("description"),
                        genre_image=request.FILES.get("image"),
                        genre_added_by=user,
                        genre_accepted_by=user
                    )
                    message = "Dodano nowy gatunek"
                    genres = Genre.objects.all().order_by("name")
                    waiting_genres = len([i for i in Genre.objects.all() if i.genre_accepted_by == None])
                    ctx = {
                        "message": message,
                        "genres": genres,
                        "waiting_genres": waiting_genres
                    }
                    return render(request, "genres.html", ctx)
                else:
                    genre = Genre.objects.create(
                        name=genre,
                        genre_description=request.POST.get("description"),
                        genre_image=request.FILES.get("image"),
                        genre_added_by=user
                    )
                    message = "Twoja propozycja czeka na akceptację"
                    genres = Genre.objects.all().order_by("name")
                    waiting_genres = len([i for i in Genre.objects.all() if i.genre_accepted_by == None])
                    ctx = {
                        "message": message,
                        "genres": genres,
                        "waiting_genres": waiting_genres
                    }
                    return render(request, "genres.html", ctx)


class GenreDetailsView(View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        articles = [i for i in Article.objects.filter(genre__id=id)]
        articles_check = len(articles)
        ctx = {
            "genre": genre,
            "articles": articles,
            "articles_check": articles_check
        }
        return render(request, "genre_details.html", ctx)


class EditGenreView(StaffMemberCheck, View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        initial_data = {
            "name": genre.name,
            "description": genre.genre_description
        }
        form = EditGenreForm(initial=initial_data)
        ctx = {
            "genre": genre,
            "form": form
        }
        return render(request, "edit_genre.html", ctx)
    
    def post(self, request, id):
        form = EditGenreForm(request.POST)
        if form.is_valid():
            genre = Genre.objects.get(id=id)
            genre_name = genre.name.title()
            genres = [i.name.title() for i in Genre.objects.all()]
            if genre.name in genres:
                genres.remove(genre.name)
            genre_name = request.POST.get("name").title()
            if genre_name in genres:
                initial_data = {
                    "name": genre.name,
                    "description": genre.genre_description
                }
                form = EditGenreForm(initial=initial_data)
                ctx = {
                    "message": f"Gatunek {genre_name} już jest w bazie.",
                    "genre": genre,
                    "form": form,
                    "data": request.POST
                }
                return render(request, "edit_genre.html", ctx)
            user = User.objects.get(pk=int(request.session.get("user_id")))
            genre.name = request.POST.get("name")
            genre.genre_description = request.POST.get("description")
            genre.genre_edited_by = user
            if request.FILES.get("image") != None or request.POST.get("delete_image"):
                genre.genre_image = request.FILES.get("image")
            if user.is_superuser and not genre.genre_accepted_by:
                genre.genre_accepted_by = user
            genre.save()
            message = "Edycja zakończona sukcesem"
            initial_data = {
                "name": genre.name,
                "description": genre.genre_description
            }
            form = EditGenreForm(initial=initial_data)
            ctx = {
                "genre": genre,
                "form": form,
                "message": message
            }
            return redirect(f"/genre_details/{genre.id}")


class DeleteGenreView(SuperUserCheck, View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        return render(request, "delete_genre.html", {"genre": genre})
    
    def post(self, request, id):
        genre = Genre.objects.get(id=id)
        genre.delete()
        return redirect("/genres")


class WaitingGenresView(SuperUserCheck, View):
    def get(self, request):
        genres = Genre.objects.all().order_by("name")
        return render(request, "waiting_genres.html", {"genres": genres})


class AcceptGenreView(SuperUserCheck, View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        return render(request, "accept_genre.html", {"genre": genre})
    
    def post(self, request, id):
        genre = Genre.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        genre.genre_accepted_by = user
        genre.save()
        return redirect("/waiting_genres")


class PeopleView(View):
    def get(self, request):
        people = Person.objects.all().order_by("last_name")
        waiting_people = len([i for i in people if i.person_accepted_by == None])
        ctx = {
            "people": people,
            "waiting_people": waiting_people
        }
        return render(request, "people.html", ctx)


class WaitingPeopleView(StaffMemberCheck, View):
    def get(self, request):
        people = Person.objects.all().order_by("last_name")
        return render(request, "waiting_people.html", {"people": people})


class PersonDetailsView(View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        user_rating = None
        personrating = PersonRating.objects.filter(person=id)
        for i in personrating:
            if i.user == user:
                user_rating = i.rating
        form = RatingForm()
        articles = [i for i in Article.objects.filter(person__id=id)]
        articles_check = len(articles)
        ctx = {
            "person": person,
            "form": form,
            "user_rating": user_rating,
            "rating": person.person_rating,
            "articles": articles,
            "articles_check": articles_check
        }
        return render(request, "person_details.html", ctx)
    
    def post(self, request, id):
        form = RatingForm(request.POST)
        if form.is_valid():
            person = Person.objects.get(id=id)
            user = User.objects.get(pk=int(request.session.get("user_id")))
            user_rating = int(request.POST.get("rating"))
            rating = Rating.objects.get(id=user_rating)
            personrating = PersonRating.objects.create(user=user, rating=rating, person=person)
            person_rating = person.person_rating
            new_rating = rating.rating
            if person_rating != None:
                new_rating = round((rating.rating+person_rating)/2, 2)
            person.person_rating = new_rating
            person.save()
        return redirect(f"/person_details/{person.id}")


class SearchPersonView(View):
    def get(self, request):
        form = SearchPersonForm()
        return render(request, "search_person.html", {"form": form})

    def post(self, request):
        form = SearchPersonForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            persons = Person.objects.filter(last_name__icontains=text).order_by(
                "last_name"
            )

            ctx = {
                "form": form,
                "persons": persons,
                "post": request.POST
                }
            return render(request, "search_movie.html", ctx)


class AddPersonView(ActivateUserCheck, View):
    def get(self, request):
        form = AddPersonForm()
        return render(request, "add_person.html", {"form": form})

    def post(self, request):
        form = AddPersonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            names = [f"{i.first_name} {i.last_name}" for i in Person.objects.all()]
            name = f"{data['first_name'].title()} {data['last_name'].title()}"
            if name in names:
                ctx = {
                    "error_message": "Taka osoba jest już w bazie.",
                    "form": form,
                    "data": request.POST
                }
                return render(request, "add_person.html", ctx)
            else:
                user = User.objects.get(pk=int(request.session.get("user_id")))
                if user.is_staff == True:
                    person = Person.objects.create(
                        first_name=request.POST.get("first_name"),
                        last_name=request.POST.get("last_name"),
                        person_description=request.POST.get("description"),
                        person_image=request.FILES.get("image"),
                        person_added_by=user,
                        person_accepted_by=user
                    )
                    message = "Dodano nową osobę"
                    people = Person.objects.all().order_by("last_name")
                    waiting_people = len([i for i in Person.objects.all() if i.person_accepted_by == None])
                    ctx = {
                        "message": message,
                        "people": people,
                        "waiting_people": waiting_people
                    }
                    return render(request, "people.html", ctx)
                else:
                    person = Person.objects.create(
                        first_name=request.POST.get("first_name"),
                        last_name=request.POST.get("last_name"),
                        person_description=request.POST.get("description"),
                        person_image=request.FILES.get("image"),
                        person_added_by=user
                    )
                    message = "Twoja propozycja czeka na akceptację"
                    people = Person.objects.all().order_by("last_name")
                    waiting_people = len([i for i in Person.objects.all() if i.person_accepted_by == None])
                    ctx = {
                        "message": message,
                        "people": people,
                        "waiting_people": waiting_people
                    }
                    return render(request, "people.html", ctx)


class EditPersonView(StaffMemberCheck, View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        initial_data = {
            "first_name": person.first_name,
            "last_name": person.last_name,
            "description": person.person_description
        }
        form = EditPersonForm(initial=initial_data)
        ctx = {
            "person": person,
            "form": form
        }
        return render(request, "edit_person.html", ctx)
    
    def post(self, request, id):
        form = EditPersonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            person = Person.objects.get(id=id)
            names = [f"{i.first_name} {i.last_name}" for i in Person.objects.all()]
            name = f"{person.first_name.title()} {person.last_name.title()}"
            if name in names:
                names.remove(name)
            person_name = f"{request.POST.get('first_name').title()} {request.POST.get('last_name').title()}"
            if person_name in names:
                initial_data = {
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                    "description": person.person_description
                }
                form = EditPersonForm(initial=initial_data)
                ctx = {
                    "message": f"Osoba {person_name} już jest w bazie.",
                    "person": person,
                    "form": form,
                    "data": request.POST
                }
                return render(request, "edit_person.html", ctx)
            user = User.objects.get(pk=int(request.session.get("user_id")))
            person.first_name = request.POST.get("first_name")
            person.last_name = request.POST.get("last_name")
            person.person_description = request.POST.get("description")
            person.person_edited_by = user
            if request.FILES.get("image") != None or request.POST.get("delete_image"):
                person.person_image = request.FILES.get("image")
            if user.is_staff and not person.person_accepted_by:
                person.person_accepted_by = user
            person.save()
            message = "Edycja zakończona sukcesem"
            initial_data = {
                "first_name": person.first_name,
                "last_name": person.last_name,
                "description": person.person_description
            }
            form = EditPersonForm(initial=initial_data)
            ctx = {
                "person": person,
                "form": form,
                "message": message
            }
            return redirect(f"/person_details/{person.id}")


class DeletePersonView(StaffMemberCheck, View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        return render(request, "delete_person.html", {"person": person})
    
    def post(self, request, id):
        person = Person.objects.get(id=id)
        person.delete()
        return redirect("/people")


class AcceptPersonView(StaffMemberCheck, View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        return render(request, "accept_person.html", {"person": person})
    
    def post(self, request, id):
        person = Person.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        person.person_accepted_by = user
        person.save()
        return redirect("/waiting_people")


class AddArticleGenreView(StaffMemberCheck, View):
    def get(self, request, id):
        genre = Genre.objects.get(id=id)
        form = AddArticleForm()
        ctx = {
            "genre": genre,
            "form": form
        }
        return render(request, "add_article_genre.html", ctx)
    
    def post(self, request, id):
        form = AddArticleForm(request.POST)
        genre = Genre.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        message = "Coś poszło nie tak"
        if form.is_valid():
            data = form.cleaned_data
            links = [i.link for i in Article.objects.all()]
            if data["url"] in links:
                message = "Taki link jest już w naszym archiwum."
                ctx = {
                    "form": form,
                    "genre": genre,
                    "message": message
                }
                return render(request, "add_article_genre.html", ctx)
            article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"])
            genre.genre_article.add(article)
            genre.save()
            message = "Artykuł dodany pomyślnie"
            ctx = {
                "form": form,
                "genre": genre,
                "article": article,
                "message": message
            }
            return redirect(f"/genre_details/{genre.id}")
        ctx = {
            "form": form,
            "genre": genre,
            "message": message
        }
        return render(request, "add_article_genre.html", ctx)


class DeleteArticleGenreView(StaffMemberCheck, View):
    def get(self, request, genre_id, article_id):
        genre = Genre.objects.get(id=genre_id)
        article = Article.objects.get(id=article_id)
        ctx = {
            "genre": genre,
            "article": article
        }
        return render(request, "delete_article_genre.html", ctx)
    
    def post(self, request, genre_id, article_id):
        article = Article.objects.get(id=article_id)
        article.delete()
        message = "Artykuł został usunięty."
        return redirect(f"/genre_details/{genre_id}")


class AddArticlePersonView(StaffMemberCheck, View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        form = AddArticleForm()
        ctx = {
            "person": person,
            "form": form
        }
        return render(request, "add_article_person.html", ctx)
    
    def post(self, request, id):
        form = AddArticleForm(request.POST)
        person = Person.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        message = "Coś poszło nie tak"
        if form.is_valid():
            data = form.cleaned_data
            links = [i.link for i in Article.objects.all()]
            if data["url"] in links:
                message = "Taki link jest już w naszym archiwum."
                ctx = {
                    "form": form,
                    "person": person,
                    "message": message
                }
                return render(request, "add_article_person.html", ctx)
            article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"])
            person.person_article.add(article)
            person.save()
            message = "Artykuł dodany pomyślnie"
            ctx = {
                "form": form,
                "person": person,
                "article": article,
                "message": message
            }
            return redirect(f"/person_details/{person.id}")
        ctx = {
            "form": form,
            "person": person,
            "message": message
        }
        return render(request, "add_article_person.html", ctx)


class DeleteArticlePersonView(StaffMemberCheck, View):
    def get(self, request, person_id, article_id):
        person = Person.objects.get(id=person_id)
        article = Article.objects.get(id=article_id)
        ctx = {
            "person": person,
            "article": article
        }
        return render(request, "delete_article_person.html", ctx)
    
    def post(self, request, person_id, article_id):
        article = Article.objects.get(id=article_id)
        article.delete()
        message = "Artykuł został usunięty."
        return redirect(f"/person_details/{person_id}")