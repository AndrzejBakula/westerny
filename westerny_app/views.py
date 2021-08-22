from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.urls import reverse
from datetime import timezone, date, timedelta
from .utils import token_generator
from django.views import View
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from westerny_project.settings import PROTOCOLE
from westerny_app.models import Movie, Genre, Person, Article, Rank, UserRank, PersonRating, Rating, MovieRating
from westerny_app.models import PersonMovie, Counter, Deleted
from westerny_app.forms import AddMovieForm, AddGenreForm, AddPersonForm, EditGenreForm, RegisterForm, LoginForm
from westerny_app.forms import SearchMovieForm, SearchPersonForm, AddArticleForm, EditPersonForm, RatingForm
from westerny_app.forms import EditMovieForm, AddActorForm, ResetForm


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

    movies = Movie.objects.filter(movie_added_by=user)
    added_movies = len([i for i in movies if i.movie_accepted_by])*2
    people = Person.objects.filter(person_added_by=user)
    added_people = len([i for i in people if i.person_accepted_by])
    genres = Genre.objects.filter(genre_added_by=user)
    added_genre = len([i for i in genres if i.genre_accepted_by])
    sum_of_added = added_genre+added_movies+added_people

    accpted_movies = len(Movie.objects.filter(movie_accepted_by=user))
    accepted_people = len(Person.objects.filter(person_accepted_by=user))
    accepted_genre = len(Genre.objects.filter(genre_accepted_by=user))
    sum_of_accepted = added_genre+accepted_people+accpted_movies

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
        if ( 25 <= sum_of_accepted < 75):
            userrank.rank = kapitan
            return userrank.save()
        elif (75 <= sum_of_accepted < 150):
            userrank.rank = major
            return userrank.save()
        elif sum_of_accepted >= 150:
            userrank.rank = pulkownik
            return userrank.save()
        return userrank.save()
    elif user.is_superuser == True:
        userrank.rank = general
        return userrank.save()       


def validate_email(email):
    for i in User.objects.all():
        if i.email == email:
            return True
    return False


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
        counter = Counter.objects.all()[0]
        counter.counter += 1
        counter.save()
        last_movies = [i for i in Movie.objects.all().order_by("-id") if i.movie_accepted_by != None][:3]
        last_people = [i for i in Person.objects.all().order_by("-id") if i.person_accepted_by != None][:3]
        last_articles = [i for i in Article.objects.all().order_by("-id") if i.is_accepted == True][:2]
        waiting_movies = Movie.objects.filter(movie_accepted_by=None)
        waiting_people = Person.objects.filter(person_accepted_by=None)
        waiting_articles = Article.objects.filter(is_accepted=False)
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
            check_rank(user)
            promotion_asks = len(UserRank.objects.filter(promotion_ask=True))
            ctx = {
                "promotion_asks": promotion_asks,
                "last_movies": last_movies,
                "last_people": last_people,
                "last_articles": last_articles,
                "waiting_movies": waiting_movies,
                "waiting_people": waiting_people,
                "waiting_articles": waiting_articles
            }
            return render(request, "index.html", ctx)
        ctx = {
            "last_movies": last_movies,
            "last_people": last_people,
            "last_articles": last_articles
        }
        return render(request, "index.html", ctx)


class RulesView(View):
    def get(self, request):
        return render(request, "rules.html")


class RegisterView(View):

    FORBIDDEN = ("westerny", "Westerny", "WESTERNY", "WeStErNy", "wEsTeRnY", "west", "West", "WEST",
                "Westernowy", "WESTERNOWY", "westernowy", "Westernowo", "westernowo", "WESTERNOWO",
                "western", "WESTERN", "Western", "westerns", "Westerns", "WESTERNS")

    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})
    
    def post(self, request):
        users = [i.username for i in User.objects.all()]
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
        elif username in self.FORBIDDEN:
            message = "Taką nazwę nosi poszukiwany listem gończym bandyta."
            ctx = {
                "email": email,
                "message": message,
                "form": form
            }
            return render(request, "register.html", ctx)
        elif validate_email(email):
            message = "Ta skrzynka na listy jest już zajęta."
            ctx = {
                "username": username,
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
        message = 'Niepoprawne dane logowania. Rejestracja dostępna w sekcji "nabór".'
        ctx = {
            "message": message,
            "form": LoginForm(request.POST)
        }
        return render(request, "login.html", ctx)


class LogoutView(ActivateUserCheck, View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            request.session["logged"] = False
        return redirect("/index")


class RequestPasswordResetEmail(View):
    def get(self, request):        
        return render(request, 'registration/reset_password.html')
    
    def post(self, request):
        email = request.POST['email']
        
        if not validate_email(email):
            message = "Podaj właściwą skrzynkę pocztową."
            ctx = {
            "values": request.POST,
            "message": message
        }
            return render(request, 'registration/reset_password.html', ctx)
        
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }
        link = reverse('set-new-password', kwargs={
            'uidb64': email_contents['uid'], 'token': email_contents['token']})
        email_subject = "Resetowanie hasła"
        reset_url = PROTOCOLE+current_site.domain+link
        email = EmailMessage(
            email_subject,
            "Baczność! Należy kliknąć w poniższy link \n" + reset_url,
            "noreply@semycolon.com",
            [user[0].email],
        )
        email.send(fail_silently=False)  
        message = "Generalicja wysłała do ciebie list intencyjny."
        ctx = {
            "message": message
        }
        return render(request, 'registration/reset_password.html', ctx)


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        form = ResetForm()

        try:
            user_id = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                message = "Użyto niewłaściwego listu intencyjnego. Wystąp o nowy."
                return render(request, "registration/set_new_password.html", {"message": message})
        except Exception as identifier:
            pass

        ctx = {
            "uidb64": uidb64,
            "token": token,
            "form": form,
        }
        return render(request, "registration/set_new_password.html", ctx)
    
    def post(self, request, uidb64, token):
        form = ResetForm(request.POST)
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password != password2:
            error_message = "Proszę podać dwa takie same hasła."
            ctx = {
                "uidb64": uidb64,
                "token": token,
                "error_message": error_message,
                "form": form
            }
            return render(request, "registration/set_new_password.html", ctx)
        elif len(password) < 6:
            error_message = "Hasło powinno mieć przynajmniej 6 znaków."
            ctx = {
                "uidb64": uidb64,
                "token": token,
                "error_message": error_message,
                "form": form
            }
            return render(request, "registration/set_new_password.html", ctx)
        try:
            user_id = urlsafe_base64_decode(uidb64)
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            message = "Hasło zostało ustawione."
            ctx = {
                "message": message
            }
            return render(request, "registration/set_new_password.html", ctx)
        except Exception as identifier:
            message = "Coś poszło nie tak, spróbuj ponownie."
            ctx = {
                "message": message
            }
            return render(request, "registration/set_new_password.html", ctx)


class MyPlaceView(ActivateUserCheck, View):
    def get(self, request):
        user = User.objects.get(pk=request.session.get("user_id"))
        check_rank(user)
        added_westerns = len(Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False))
        added_people = len(Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False))
        added_genres = len(Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False))
        links = len(Article.objects.filter(article_added_by=user, is_accepted=True))
        roles = len(PersonMovie.objects.filter(personmovie_added_by=user))
        ratings = len(PersonRating.objects.filter(user=user)) + len(MovieRating.objects.filter(user=user))
        notes = added_westerns + added_people + added_genres + links
        rejected = Deleted.objects.filter(added_by=user)

        accepted_westerns = len(Movie.objects.filter(movie_accepted_by=user))
        accepted_people = len(Person.objects.filter(person_accepted_by=user))
        accepted_genres = len(Genre.objects.filter(genre_accepted_by=user))
        accepted_notes = accepted_westerns + accepted_people + accepted_genres
        deleted = Deleted.objects.filter(deleted_by=user)

        userrank = UserRank.objects.get(user=user.id).rank

        kawalerzysta = Rank.objects.get(name="kawalerzysta")
        kapral = Rank.objects.get(name="kapral")
        sierzant = Rank.objects.get(name="sierżant")
        porucznik = Rank.objects.get(name="porucznik")
        kapitan = Rank.objects.get(name="kapitan")
        major = Rank.objects.get(name="major")
        pulkownik = Rank.objects.get(name="pułkownik")
        general = Rank.objects.get(name="generał")
        gubernator = Rank.objects.get(name="gubernator")

        promotion_add = None
        promotion_accept = None
        promotion_ask = False
        if UserRank.objects.get(user=user).promotion_ask == True:
            promotion_ask = None
        added_points = added_westerns*2 + added_people
        accepted_points = accepted_westerns + accepted_people + added_genres
        if userrank == kawalerzysta:
            promotion_add = 10-added_points
        elif userrank == kapral:
            promotion_add = 30-added_points
        elif userrank == sierzant:
            promotion_add = 50-added_points
            if UserRank.objects.get(user=user).promotion_ask == False and added_points >= 50:
                promotion_ask = True
        elif userrank == porucznik:
            promotion_accept = 25-accepted_points
        elif userrank == kapitan:
            promotion_accept = 75-accepted_points
        elif userrank == major:
            promotion_accept = 150-accepted_points
        elif userrank == pulkownik:
            promotion_accept = 250-accepted_points
            if accepted_points >= 250 and UserRank.objects.get(user=user).promotion_ask == False:
                promotion_ask = True

        waiting_people = Person.objects.filter(person_accepted_by=None, person_added_by=user)
        waiting_movies = Movie.objects.filter(movie_accepted_by=None, movie_added_by=user)
        waiting_articles = Article.objects.filter(article_added_by=user, is_accepted=False)

        my_movies = Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False)
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)

        rated_movies = MovieRating.objects.filter(user=user)
        rated_people = PersonRating.objects.filter(user=user)

        ctx = {
            "westerns": added_westerns,
            "people": added_people,
            "genres": added_genres,
            "notes": notes,
            "links": links,
            "roles": roles,
            "ratings": ratings,
            "accepted_westerns": accepted_westerns,
            "accepted_people": accepted_people,
            "accepted_genres": accepted_genres,
            "accepted_notes": accepted_notes,
            "promotion_add": promotion_add,
            "promotion_accept": promotion_accept,
            "promotion_ask": promotion_ask,
            "userrank": UserRank.objects.get(user=user),
            "waiting_people": waiting_people,
            "waiting_movies": waiting_movies,
            "waiting_articles": waiting_articles,
            "my_movies": my_movies,
            "my_people": my_people,
            "my_genres": my_genres,
            "deleted": deleted,
            "rejected": rejected,
            "rated_movies": rated_movies,
            "rated_people": rated_people
        }
        return render(request, "my_place.html", ctx)
    
    def post(self, request):
        user = User.objects.get(pk=request.session.get("user_id"))
        userrank = UserRank.objects.get(user=user)
        userrank.promotion_ask = True
        userrank.save()
        return redirect("/my_place")


class RatedMoviesView(ActivateUserCheck, View):
    def get(self, request):
        user = User.objects.get(pk=request.session.get("user_id"))
        rated_movies = MovieRating.objects.filter(user=user).order_by("-rating__rating", "movie__year")
        rated_people = PersonRating.objects.filter(user=user)
        my_movies = Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False)
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)

        paginator = Paginator(rated_movies, 10)
        page = request.GET.get("page")
        rated_movies = paginator.get_page(page)

        ctx = {
            "rated_movies": rated_movies,
            "rated_people": rated_people,
            "my_movies": my_movies,
            "my_people": my_people,
            "my_genres": my_genres
        }
        return render(request, "rated_movies.html", ctx)


class RatedPeopleView(ActivateUserCheck, View):
    def get(self, request):
        user = User.objects.get(pk=request.session.get("user_id"))
        rated_people = PersonRating.objects.filter(user=user).order_by("-rating__rating", "person__last_name")
        rated_movies = MovieRating.objects.filter(user=user)
        my_movies = Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False)
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)

        paginator = Paginator(rated_people, 10)
        page = request.GET.get("page")
        rated_people = paginator.get_page(page)

        ctx = {
            "rated_movies": rated_movies,
            "rated_people": rated_people,
            "my_movies": my_movies,
            "my_people": my_people,
            "my_genres": my_genres
        }
        return render(request, "rated_people.html", ctx)


class UserDetailsView(View):
    def get(self, request, id):
        soldier = User.objects.get(pk=id)
        check_rank(soldier)
        westerns = Movie.objects.filter(movie_added_by=soldier, movie_accepted_by__isnull=False)
        westerns_count = len([i for i in westerns if i.movie_accepted_by])
        people = Person.objects.filter(person_added_by=soldier, person_accepted_by__isnull=False)
        people_count = len([i for i in people if i.person_accepted_by])
        genres = Genre.objects.filter(genre_added_by=soldier, genre_accepted_by__isnull=False)
        genres_count = len([i for i in genres if i.genre_accepted_by])
        links = len(Article.objects.filter(article_added_by=soldier))
        roles = len(PersonMovie.objects.filter(personmovie_added_by=soldier))
        ratings = len(PersonRating.objects.filter(user=soldier)) + len(MovieRating.objects.filter(user=soldier))
        notes = westerns_count + people_count + genres_count + links
        rejected = Deleted.objects.filter(added_by=soldier)

        accepted_westerns = len(Movie.objects.filter(movie_accepted_by=soldier))
        accepted_people = len(Person.objects.filter(person_accepted_by=soldier))
        accepted_genres = len(Genre.objects.filter(genre_accepted_by=soldier))
        accepted_notes = accepted_westerns + accepted_people + accepted_genres
        deleted = Deleted.objects.filter(deleted_by=soldier)

        userrank = UserRank.objects.get(user=soldier)

        ctx = {
            "soldier": soldier,
            "westerns_count": westerns_count,
            "people_count": people_count,
            "genres_count": genres_count,
            "notes": notes,
            "links": links,
            "roles": roles,
            "ratings": ratings,
            "accepted_westerns": accepted_westerns,
            "accepted_people": accepted_people,
            "accepted_genres": accepted_genres,
            "accepted_notes": accepted_notes,
            "userrank": userrank,
            "deleted": deleted,
            "rejected": rejected
        }
        return render(request, "user_details.html", ctx)



class AddedMoviesView(View):
    def get(self, request, id):
        soldier = User.objects.get(pk=id)
        movies = Movie.objects.filter(movie_accepted_by__isnull=False, movie_added_by=soldier).order_by("year")
        my_people = Person.objects.filter(person_added_by=soldier, person_accepted_by__isnull=False).order_by("last_name")
        my_genres = Genre.objects.filter(genre_added_by=soldier, genre_accepted_by__isnull=False).order_by("name")

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "soldier": soldier,
            "movies": movies,
            "my_people": my_people,
            "my_genres": my_genres
        }
        return render(request, "added_movies.html", ctx)
    

class AddedPeopleView(View):
    def get(self, request, id):
        soldier = User.objects.get(pk=id)
        people = Person.objects.filter(person_added_by=soldier, person_accepted_by__isnull=False).order_by("last_name")
        my_movies = Movie.objects.filter(movie_added_by=soldier, movie_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=soldier, genre_accepted_by__isnull=False)

        paginator = Paginator(people, 10)
        page = request.GET.get("page")
        people = paginator.get_page(page)

        ctx = {
            "soldier": soldier,
            "people": people,
            "my_movies": my_movies,
            "my_genres": my_genres
        }
        return render(request, "added_people.html", ctx)


class AddedGenresView(View):
    def get(self, request, id):
        soldier = User.objects.get(pk=id)
        my_movies = Movie.objects.filter(movie_accepted_by__isnull=False, movie_added_by=soldier)
        my_people = Person.objects.filter(person_added_by=soldier, person_accepted_by__isnull=False)
        genres = Genre.objects.filter(genre_added_by=soldier, genre_accepted_by__isnull=False).order_by("name")

        paginator = Paginator(genres, 10)
        page = request.GET.get("page")
        genres = paginator.get_page(page)

        ctx = {
            "soldier": soldier,
            "genres": genres,
            "my_movies": my_movies,
            "my_people": my_people
        }
        return render(request, "added_genres.html", ctx)


class GivePromotionView(SuperUserCheck, View):
    def get(self, request, id):
        soldier = User.objects.get(id=id)
        userrank = UserRank.objects.get(user=soldier)
        ctx = {
            "userrank": userrank,
            "soldier": soldier
        }
        return render(request, "give_promotion.html", ctx)
    
    def post(self, request, id):
        soldier = User.objects.get(id=id)
        userrank = UserRank.objects.get(user=soldier)
        rank = Rank.objects.get(name="porucznik")
        userrank.rank = rank
        userrank.promotion_ask = False
        soldier.is_staff = True
        userrank.save()
        soldier.save()
        message = "Awans przyznany"
        return render(request, "give_promotion.html", {"message": message})


class PromotionAsksView(ActivateUserCheck, View):
    def get(self, request):
        promotion_asks = UserRank.objects.filter(promotion_ask=True)
        return render(request, "promotion_asks.html", {"promotion_asks": promotion_asks})


class StatsView(View):
    def get(self, request):
        counter = Counter.objects.all()[0]
        civils = User.objects.filter(is_active=False)
        users = len([i for i in User.objects.filter(is_active=True)]) - 3
        fort = len(civils) + users
        officers = len([i for i in User.objects.filter(is_staff=True, is_superuser=False) if i.username != "westerny"])
        commanders = User.objects.filter(is_superuser=True)
        cavaliers = len([i for i in User.objects.filter(is_active=True, is_staff=False, is_superuser=False) if i.username not in ("west", "Andrzej Bakuła")])
        westerns = Movie.objects.filter(movie_accepted_by__isnull=False)
        people = Person.objects.filter(person_accepted_by__isnull=False)
        genres = Genre.objects.filter(genre_accepted_by__isnull=False)
        notes = len(westerns) + len(people) + len(genres)
        links = Article.objects.filter(is_accepted=True)
        waiting_movies = Movie.objects.filter(movie_accepted_by=None)
        waiting_people = Person.objects.filter(person_accepted_by=None)
        waiting_articles = Article.objects.filter(is_accepted=False)
        movie_ratings = len([i for i in MovieRating.objects.all()])
        people_ratings = len([i for i in PersonRating.objects.all()])
        ratings = movie_ratings + people_ratings
        roles = len([i for i in PersonMovie.objects.all()])
        last_movie_ratings = [i for i in MovieRating.objects.all().order_by("-id")][:3]
        last_person_ratings = [i for i in PersonRating.objects.all().order_by("-id")][:3]
        newest_soldier = User.objects.all().order_by("-id")[0]
        last_roles = PersonMovie.objects.all().order_by("-id")[:2]

        ctx = {
            "civils": civils,
            "users": users,
            "fort": fort,
            "officers": officers,
            "commanders": commanders,
            "cavaliers": cavaliers,
            "westerns": westerns,
            "people": people,
            "genres": genres,
            "notes": notes,
            "links": links,
            "counter": counter,
            "waiting_movies": waiting_movies,
            "waiting_people": waiting_people,
            "waiting_articles": waiting_articles,
            "ratings": ratings,
            "roles": roles,
            "last_person_ratings": last_person_ratings,
            "last_movie_ratings": last_movie_ratings,
            "newest_soldier": newest_soldier,
            "last_roles": last_roles
        }
        return render(request, "stats.html", ctx)


class MoviesView(View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        movies = Movie.objects.filter(movie_accepted_by__isnull=False).order_by("year")
        waiting_movies = len([i for i in Movie.objects.filter(movie_accepted_by=None)])
        waiting_movies_user = len([i for i in Movie.objects.filter(movie_accepted_by=None) if i.movie_added_by == user])
        waiting_articles = len([i for i in Article.objects.filter(is_accepted=False) if len(i.movie_set.all()) > 0])

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "movies": movies,
            "waiting_movies": waiting_movies,
            "waiting_movies_user": waiting_movies_user,
            "waiting_articles": waiting_articles
        }
        return render(request, "movies.html", ctx)


class MoviesNewestView(View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        movies = Movie.objects.filter(movie_accepted_by__isnull=False).order_by("-id")
        waiting_movies = len([i for i in Movie.objects.filter(movie_accepted_by=None)])
        waiting_movies_user = len([i for i in Movie.objects.filter(movie_accepted_by=None) if i.movie_added_by == user])
        waiting_articles = len([i for i in Article.objects.filter(is_accepted=False) if len(i.movie_set.all()) > 0])

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "movies": movies,
            "waiting_movies": waiting_movies,
            "waiting_movies_user": waiting_movies_user,
            "waiting_articles": waiting_articles
        }
        return render(request, "movies_newest.html", ctx)


class MyMoviesView(ActivateUserCheck, View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        movies = Movie.objects.filter(movie_accepted_by__isnull=False, movie_added_by=user).order_by("year")
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)
        rated_movies = MovieRating.objects.filter(user=user)
        rated_people = PersonRating.objects.filter(user=user)

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "movies": movies,
            "my_people": my_people,
            "my_genres": my_genres,
            "rated_movies": rated_movies,
            "rated_people": rated_people
        }
        return render(request, "my_movies.html", ctx)
    

class WaitingMoviesView(StaffMemberCheck, View):
    def get(self, request):
        movies = Movie.objects.filter(movie_accepted_by=None).order_by("year")
        movie_waiting_articles = set([i.movie_set.all()[0] for i in Article.objects.filter(is_accepted=False) if len(i.movie_set.all()) > 0])
        waiting_articles = len(movie_waiting_articles)

        ctx = {
            "movies": movies,
            "movie_waiting_articles": movie_waiting_articles,
            "waiting_articles": waiting_articles
        }

        return render(request, "waiting_movies.html", ctx)


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

            paginator = Paginator(movies, 10)
            page = request.GET.get("page")
            movies = paginator.get_page(page)

            ctx = {
                "form": form,
                "movies": movies,
                "post": request.POST
                }
            return render(request, "search_movie.html", ctx)


class SearchMyMovieView(ActivateUserCheck, View):
    def get(self, request):
        form = SearchMovieForm()
        return render(request, "search_my_movie.html", {"form": form})

    def post(self, request):
        form = SearchMovieForm(request.POST)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if form.is_valid():
            text = form.cleaned_data["text"]
            movies = Movie.objects.filter(title__icontains=text, movie_added_by=user).order_by(
                "title"
            )

            paginator = Paginator(movies, 10)
            page = request.GET.get("page")
            movies = paginator.get_page(page)

            ctx = {
                "form": form,
                "movies": movies,
                "post": request.POST
                }
            return render(request, "search_my_movie.html", ctx)


class MoviesRankView(View):
    def get(self, request):
        movies = Movie.objects.filter(movie_accepted_by__isnull=False, movie_rating__isnull=False).annotate(num_movies=Count("movierating")).order_by("-movie_rating", "-num_movies", "title")

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "movies": movies
        }
        return render(request, "movies_rank.html", ctx)


class AddMovieView(ActivateUserCheck, View):
    def get(self, request):
        form = AddMovieForm()
        return render(request, "add_movie.html", {"form": form})
    
    def post(self, request):
        form = AddMovieForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = data["title"].title()
            org_title = data["org_title"].title()
            year = data["year"]
            director = data["director"]
            screenplay = data["screenplay"]
            music = data["music"]
            cinema = data["cinema"]
            genre = data["genre"]
            description = data["description"]
            image = request.FILES.get("image")
            titles = [i.title.title() for i in Movie.objects.all()]
            if title in titles:
                ctx = {
                    "error_message": "Taki western jest już w bazie.",
                    "form": form,
                    "data": request.POST
                }
                return render(request, "add_movie.html", ctx)
            else:
                user = User.objects.get(pk=int(request.session.get("user_id")))
                if user.is_staff == True:
                    movie = Movie.objects.create(
                        title=data["title"],
                        year=year,
                        movie_description=data["description"],
                        movie_image=request.FILES.get("image"),
                        movie_added_by=user,
                        movie_accepted_by=user
                    )
                    for i in director:
                        movie.director.add(i)
                    for i in screenplay:
                        movie.screenplay.add(i)
                    for i in music:
                        movie.music.add(i)
                    for i in cinema:
                        movie.cinema.add(i)
                    for i in genre:
                        movie.genre.add(i)
                    if data["org_title"] not in ("", None):
                        movie.org_title = data["org_title"]
                    movie.save()
                    message = "Dodano nowy western"
                    ctx = {
                        "message": message,
                    }
                    return render(request, "add_movie.html", ctx)
                else:
                    movie = Movie.objects.create(
                        title=data["title"],
                        year=year,
                        movie_description=data["description"],
                        movie_image=request.FILES.get("image"),
                        movie_added_by=user
                    )
                    for i in director:
                        movie.director.add(i)
                    for i in screenplay:
                        movie.screenplay.add(i)
                    for i in music:
                        movie.music.add(i)
                    for i in cinema:
                        movie.cinema.add(i)
                    for i in genre:
                        movie.genre.add(i)
                    if data["org_title"] not in ("", None):
                        movie.org_title = data["org_title"]
                    movie.save()
                    message = "Twoja propozycja czeka na akceptację"
                    ctx = {
                        "message": message,
                    }
                    return render(request, "add_movie.html", ctx)


class MovieDetailsView(View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        user_rating = None
        rating = None
        movierating = MovieRating.objects.filter(movie=id)
        sum_movierating = round(sum([i.rating.rating for i in movierating]), 2)
        if len(movierating) > 0:
            rating = round(sum_movierating/len(movierating), 2)
        for i in movierating:
            if i.user == user:
                user_rating = i.rating
        form = RatingForm()
        articles = Article.objects.filter(movie__id=id)
        user_waiting_articles = Article.objects.filter(article_added_by=user, is_accepted=False)
        ctx = {
            "movie": movie,
            "form": form,
            "user_rating": user_rating,
            "rating": rating,
            "articles": articles,
            "len_movierating": len(movierating),
            "user_waiting_articles": user_waiting_articles
        }
        return render(request, "movie_details.html", ctx)
    
    def post(self, request, id):
        form = RatingForm(request.POST)
        if form.is_valid():
            movie = Movie.objects.get(id=id)
            user = User.objects.get(pk=int(request.session.get("user_id")))
            user_rating = int(request.POST.get("rating"))
            rating = Rating.objects.get(id=user_rating)
            movierating = MovieRating.objects.create(user=user, rating=rating, movie=movie)
            rating = None
            movierating = MovieRating.objects.filter(movie=id)
            sum_movierating = round(sum([i.rating.rating for i in movierating]), 2)
            if len(movierating) > 0:
                rating = round(sum_movierating/len(movierating), 2)
            movie.movie_rating = rating
            movie.save() 
        return redirect(f"/movie_details/{movie.id}")


class EditMovieView(ActivateUserCheck, View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if (movie.movie_added_by == user and movie.movie_edited_by == None) or (movie.movie_added_by == user and not movie.movie_edited_by.is_staff) or user.is_staff:
            initial_data = {
                "title": movie.title,
                "org_title": movie.org_title,
                "year": movie.year,
                "description": movie.movie_description,
                "director": [i for i in movie.director.all()],
                "screenplay": [i for i in movie.screenplay.all()],
                "music": [i for i in movie.music.all()],
                "cinema": [i for i in movie.cinema.all()],
                "genre": [i for i in movie.genre.all()]
            }
            form = EditMovieForm(initial=initial_data)
            ctx = {
                "movie": movie,
                "form": form
            }
            return render(request, "edit_movie.html", ctx)
        return redirect("/movies")
    
    def post(self, request, id):
        form = EditMovieForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            movie = Movie.objects.get(id=id)
            title = data["title"]
            org_title = data["org_title"]
            year = data["year"]
            director = data["director"]
            screenplay = data["screenplay"]
            music = data["music"]
            cinema = data["cinema"]
            genre = data["genre"]
            description = data["description"]
            image = request.FILES.get("image")
            titles = [i.title.title() for i in Movie.objects.all()]
            title = movie.title.title()
            if title in titles:
                titles.remove(title)
            movie_title = title.title()
            if movie_title in titles:
                initial_data = {
                    "title": movie.title,
                    "org_title": org_title,
                    "year": movie.year,
                    "description": movie.movie_description,
                    "director": [i for i in movie.director.all()],
                    "screenplay": [i for i in movie.screenplay.all()],
                    "music": [i for i in movie.music.all()],
                    "cinema": [i for i in movie.cinema.all()],
                    "genre": [i for i in movie.genre.all()]
                }
                form = EditMovieForm(initial=initial_data)
                ctx = {
                    "message": "Film o tym tytule jest już w bazie.",
                    "movie": movie,
                    "form": form,
                    "data": request.POST
                }
                return render(request, "edit_movie.html", ctx)
            user = User.objects.get(pk=int(request.session.get("user_id")))
            movie.title = data["title"]
            if data["org_title"] not in ("", None):
                movie.org_title = data["org_title"]
            movie.year = data["year"]
            movie.director.set(data["director"])
            movie.screenplay.set(data["screenplay"])
            movie.music.set(data["music"])
            movie.cinema.set(data["cinema"])
            movie.genre.set(data["genre"])
            movie.movie_description = data["description"]
            movie.movie_edited_by = user
            if request.FILES.get("image") != None or request.POST.get("delete_image"):
                movie.movie_image = request.FILES.get("image")
            if user.is_staff and not movie.movie_accepted_by:
                movie.movie_accepted_by = user
            movie.save()
            message = "Edycja zakończona sukcesem"
            ctx = {
                "movie": movie,
                "message": message
            }
            return redirect(f"/movie_details/{movie.id}")


class DeleteMovieView(StaffMemberCheck, View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        return render(request, "delete_movie.html", {"movie": movie})
    
    def post(self, request, id):
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        soldier = User.objects.get(id=movie.movie_added_by.id)
        movie_ratings = MovieRating.objects.filter(movie=id)
        for i in movie_ratings:
            i.delete()
        person_movie = PersonMovie.objects.filter(movies=id)
        for i in person_movie:
            i.delete()
        articles = Article.objects.filter(movie=movie)
        for i in articles:
            i.delete()
        Deleted.objects.create(added_by=soldier, deleted_by=user)
        movie.delete()        
        email_subject = "Wpis został usunięty."
        email_body = "Baczność " + soldier.username + "! Twój wpis o " + movie.title + " został usunięty, ponieważ nie nadawał się do akceptacji."
        email = EmailMessage(
            email_subject,
            email_body,
            "noreply@semycolon.com",
            [soldier.email],
            )            
        email.send(fail_silently=False)
        return redirect("/movies")


class AcceptMovieView(StaffMemberCheck, View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        return render(request, "accept_movie.html", {"movie": movie})
    
    def post(self, request, id):
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        movie.movie_accepted_by = user
        movie.save()
        return redirect("/waiting_movies")


class GiveEditMovieView(StaffMemberCheck, View):
    def get(self, request, movie_id, soldier_id):
        movie = Movie.objects.get(id=movie_id)
        soldier = User.objects.get(id=soldier_id)
        ctx = {
            "movie": movie,
            "soldier": soldier
        }
        return render(request, "give_edit_movie.html", ctx)
    
    def post(self, request, movie_id, soldier_id):
        movie = Movie.objects.get(id=movie_id)
        soldier = User.objects.get(id=soldier_id)
        movie.movie_edited_by = soldier
        movie.save()
        return redirect(f"/movie_details/{movie_id}")


class GenresView(View):
    def get(self, request):
        genres = Genre.objects.filter(genre_accepted_by__isnull=False).order_by("name")
        waiting_genres = len([i for i in Genre.objects.filter(genre_accepted_by=None)])

        paginator = Paginator(genres, 10)
        page = request.GET.get("page")
        genres = paginator.get_page(page)

        ctx = {
            "genres": genres,
            "waiting_genres": waiting_genres
        }
        return render(request, "genres.html", ctx)


class MyGenresView(StaffMemberCheck, View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        my_movies = Movie.objects.filter(movie_accepted_by__isnull=False, movie_added_by=user).order_by("year")
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)
        rated_movies = MovieRating.objects.filter(user=user)
        rated_people = PersonRating.objects.filter(user=user)

        paginator = Paginator(genres, 10)
        page = request.GET.get("page")
        genres = paginator.get_page(page)

        ctx = {
            "genres": genres,
            "my_movies": my_movies,
            "my_people": my_people,
            "rated_movies": rated_movies,
            "rated_people": rated_people
        }
        return render(request, "my_genres.html", ctx)


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
        movies = Movie.objects.filter(genre=genre, movie_accepted_by__isnull=False).order_by("year")
        articles = [i for i in Article.objects.filter(genre__id=id)]
        articles_check = len(articles)

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "genre": genre,
            "articles": articles,
            "articles_check": articles_check,
            "movies": movies
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
        articles = Article.objects.filter(genre=genre)
        for i in articles:
            i.delete()
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
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        people = Person.objects.all().order_by("last_name")
        waiting_people = Person.objects.filter(person_accepted_by=None)
        waiting_people_user = Person.objects.filter(person_added_by=user, person_accepted_by=None)
        waiting_articles = len([i for i in Article.objects.filter(is_accepted=False) if len(i.person_set.all()) > 0])

        paginator = Paginator(people, 10)
        page = request.GET.get("page")
        people = paginator.get_page(page)

        ctx = {
            "people": people,
            "waiting_people": waiting_people,
            "waiting_people_user": waiting_people_user,
            "waiting_articles": waiting_articles
        }
        return render(request, "people.html", ctx)


class PeopleNewestView(View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        people = Person.objects.all().order_by("-id")
        waiting_people = Person.objects.filter(person_accepted_by=None)
        waiting_people_user = Person.objects.filter(person_added_by=user, person_accepted_by=None)
        waiting_articles = len([i for i in Article.objects.filter(is_accepted=False) if len(i.person_set.all()) > 0])

        paginator = Paginator(people, 10)
        page = request.GET.get("page")
        people = paginator.get_page(page)

        ctx = {
            "people": people,
            "waiting_people": waiting_people,
            "waiting_people_user": waiting_people_user,
            "waiting_articles": waiting_articles
        }
        return render(request, "people_newest.html", ctx)


class MyPeopleView(ActivateUserCheck, View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        people = Person.objects.filter(person_added_by=user).order_by("last_name")
        my_movies = Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)
        rated_movies = MovieRating.objects.filter(user=user)
        rated_people = PersonRating.objects.filter(user=user)

        paginator = Paginator(people, 10)
        page = request.GET.get("page")
        people = paginator.get_page(page)

        ctx = {
            "people": people,
            "my_movies": my_movies,
            "my_genres": my_genres,
            "rated_movies": rated_movies,
            "rated_people": rated_people
        }
        return render(request, "my_people.html", ctx)


class WaitingPeopleView(StaffMemberCheck, View):
    def get(self, request):
        people = Person.objects.filter(person_accepted_by=None).order_by("last_name")
        person_waiting_articles = set([i.person_set.all()[0] for i in Article.objects.filter(is_accepted=False) if len(i.person_set.all()) > 0])
        waiting_articles = len(person_waiting_articles)
        ctx = {
            "people": people,
            "person_waiting_articles": person_waiting_articles,
            "waiting_articles": waiting_articles
        }
        return render(request, "waiting_people.html", ctx)


class PersonDetailsView(View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        user_rating = None
        rating = None
        personrating = PersonRating.objects.filter(person=id)
        sum_personrating = round(sum([i.rating.rating for i in personrating]), 2)
        if len(personrating) > 0:
            rating = round(sum_personrating/len(personrating), 2)
        for i in personrating:
            if i.user == user:
                user_rating = i.rating
        form = RatingForm()
        articles = Article.objects.filter(person__id=id)
        user_waiting_articles = Article.objects.filter(article_added_by=user, is_accepted=False)
        ctx = {
            "person": person,
            "form": form,
            "user_rating": user_rating,
            "rating": rating,
            "articles": articles,
            "len_personrating": len(personrating),
            "user_waiting_articles": user_waiting_articles
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
            rating = None
            personrating = PersonRating.objects.filter(person=id)
            sum_personrating = round(sum([i.rating.rating for i in personrating]), 2)
            if len(personrating) > 0:
                rating = round(sum_personrating/len(personrating), 2)
            person.person_rating = rating
            person.save()                
        return redirect(f"/person_details/{person.id}")


class SearchPersonView(View):
    def get(self, request):
        form = SearchPersonForm()
        return render(request, "search_person.html", {"form": form})

    def post(self, request):
        form = SearchPersonForm(request.POST)
        if form.is_valid():
            text = request.POST.get("text")
            people = Person.objects.filter(last_name__icontains=text).order_by(
                "last_name"
            )

            paginator = Paginator(people, 10)
            page = request.GET.get("page")
            people = paginator.get_page(page)        

            ctx = {
                "form": form,
                "people": people,
                "post": request.POST
                }
            return render(request, "search_person.html", ctx)


class SearchMyPersonView(ActivateUserCheck, View):
    def get(self, request):
        form = SearchPersonForm()
        return render(request, "search_my_person.html", {"form": form})

    def post(self, request):
        form = SearchPersonForm(request.POST)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if form.is_valid():
            text = request.POST.get("text")
            people = Person.objects.filter(last_name__icontains=text, person_added_by=user).order_by(
                "last_name"
            )

            paginator = Paginator(people, 10)
            page = request.GET.get("page")
            people = paginator.get_page(page)        

            ctx = {
                "form": form,
                "people": people,
                "post": request.POST
                }
            return render(request, "search_my_person.html", ctx)


class PeopleRankView(View):
    def get(self, request):
        people = Person.objects.filter(person_rating__isnull=False, person_accepted_by__isnull=False).annotate(num_rating=Count("personrating")).order_by("-person_rating","-num_rating", "last_name")

        paginator = Paginator(people, 10)
        page = request.GET.get("page")
        people = paginator.get_page(page)

        ctx = {
            "people": people
        }
        return render(request, "people_rank.html", ctx)


class AddPersonView(ActivateUserCheck, View):
    def get(self, request):
        form = AddPersonForm()
        return render(request, "add_person.html", {"form": form})

    def post(self, request):
        form = AddPersonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            names = [f"{i.first_name.title()} {i.last_name.title()}" for i in Person.objects.all()]
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
                        date_birth=data["date_birth"],
                        person_added_by=user,
                        person_accepted_by=user
                    )
                    if data["date_death"] not in ("", None):
                        person.date_death = data["date_death"]
                    person.save()
                    message = "Dodano nową osobę"
                    people = Person.objects.all().order_by("last_name")
                    waiting_people = len([i for i in Person.objects.all() if i.person_accepted_by == None])
                    ctx = {
                        "message": message,
                        "people": people,
                        "waiting_people": waiting_people
                    }
                    return render(request, "add_person.html", ctx)
                else:
                    person = Person.objects.create(
                        first_name=request.POST.get("first_name"),
                        last_name=request.POST.get("last_name"),
                        person_description=request.POST.get("description"),
                        date_birth=data["date_birth"],
                        person_image=request.FILES.get("image"),
                        person_added_by=user
                    )
                    if data["date_death"] not in ("", None):
                        person.date_death = data["date_death"]
                    person.save()
                    message = "Twoja propozycja czeka na akceptację"
                    people = Person.objects.all().order_by("last_name")
                    waiting_people = len([i for i in Person.objects.all() if i.person_accepted_by == None])
                    ctx = {
                        "message": message,
                        "people": people,
                        "waiting_people": waiting_people
                    }
                    return render(request, "add_person.html", ctx)


class EditPersonView(ActivateUserCheck, View):
    def get(self, request, id):
        person = Person.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if (person.person_added_by == user and person.person_edited_by == None) or (person.person_added_by == user and not person.person_edited_by.is_staff) or user.is_staff:
            initial_data = {
                "first_name": person.first_name,
                "last_name": person.last_name,
                "description": person.person_description,
                "date_birth": person.date_birth,
                "date_death": person.date_death
            }
            form = EditPersonForm(initial=initial_data)
            ctx = {
                "person": person,
                "form": form
            }
            return render(request, "edit_person.html", ctx)
        return redirect("/people")
    
    def post(self, request, id):
        form = EditPersonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            person = Person.objects.get(id=id)
            names = [f"{i.first_name.title()} {i.last_name.title()}" for i in Person.objects.all()]
            name = f"{person.first_name.title()} {person.last_name.title()}"
            if name in names:
                names.remove(name)
            person_name = f"{request.POST.get('first_name').title()} {request.POST.get('last_name').title()}"
            if person_name in names:
                initial_data = {
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                    "description": person.person_description,
                    "date_birth": person.date_birth,
                    "date_death": person.date_death
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
            person.date_birth = request.POST.get("date_birth")
            if request.POST.get("date_death") not in ("", None):
                person.date_death = request.POST.get("date_death")
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
                "description": person.person_description,
                "date_birth": person.date_birth,
                "date_death": person.date_death
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
        user = User.objects.get(pk=int(request.session.get("user_id")))
        soldier = User.objects.get(id=person.person_added_by.id)
        person_ratings = PersonRating.objects.filter(person=id)
        for i in person_ratings:
            i.delete()
        articles = Article.objects.filter(person=person)
        for i in articles:
            i.delete()
        personmovies = PersonMovie.objects.filter(persons=id)
        for i in personmovies:
            i.delete()
        Deleted.objects.create(added_by=soldier, deleted_by=user)
        person.delete()
        email_subject = "Wpis został usunięty."
        email_body = "Baczność " + soldier.username + "! Twój wpis o " + person.first_name + " " + person.last_name + " został usunięty, ponieważ nie nadawał się do akceptacji."
        email = EmailMessage(
            email_subject,
            email_body,
            "noreply@semycolon.com",
            [soldier.email],
            )            
        email.send(fail_silently=False)
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


class GiveEditPersonView(StaffMemberCheck, View):
    def get(self, request, person_id, soldier_id):
        person = Person.objects.get(id=person_id)
        soldier = User.objects.get(id=soldier_id)
        ctx = {
            "person": person,
            "soldier": soldier
        }
        return render(request, "give_edit_person.html", ctx)
    
    def post(self, request, person_id, soldier_id):
        person = Person.objects.get(id=person_id)
        soldier = User.objects.get(id=soldier_id)
        person.person_edited_by = soldier
        person.save()
        return redirect(f"/person_details/{person_id}")


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
            article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"], is_accepted=True)
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


class AddArticlePersonView(ActivateUserCheck, View):
    def get(self, request, id):
        user = User.objects.get(pk=int(request.session.get("user_id")))
        person = Person.objects.get(id=id)
        waiting_articles = [i for i in Article.objects.filter(article_added_by=user, is_accepted=False)]
        if user.is_staff or 3 > len(waiting_articles):
            form = AddArticleForm()
            ctx = {
                "person": person,
                "form": form
            }
            return render(request, "add_article_person.html", ctx)
        return redirect("/people")
    
    def post(self, request, id):
        form = AddArticleForm(request.POST)
        person = Person.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        error_message = "Coś poszło nie tak"
        message = None
        if form.is_valid():
            data = form.cleaned_data
            links = [i.link for i in Article.objects.all()]
            if data["url"] in links:
                error_message = "Taki link jest już w naszym archiwum."
                ctx = {
                    "form": form,
                    "person": person,
                    "error_message": error_message
                }
                return render(request, "add_article_person.html", ctx)
            if user.is_staff:
                article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"], is_accepted=True)
                person.person_article.add(article)
                person.save()
                message = "Artykuł dodany pomyślnie."
            else:
                article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"])
                person.person_article.add(article)
                person.save()
                message = "Artykuł czeka na akceptację."
            ctx = {
                "form": form,
                "person": person,
                "article": article,
                "message": message
            }
            return render(request, "add_article_person.html", ctx)
        ctx = {
            "form": form,
            "person": person,
            "error_message": error_message
        }
        return render(request, "add_article_person.html", ctx)


class DeleteArticlePersonView(ActivateUserCheck, View):
    def get(self, request, person_id, article_id):
        user = User.objects.get(pk=int(request.session.get("user_id")))
        person = Person.objects.get(id=person_id)
        article = Article.objects.get(id=article_id)
        if user.is_superuser or user.is_staff and not article.is_accepted or article.article_added_by == user and not person.person_edited_by or article.article_added_by == user and person.person_edited_by == user:
            ctx = {
                "person": person,
                "article": article
            }
            return render(request, "delete_article_person.html", ctx)
        return redirect("/people")
    
    def post(self, request, person_id, article_id):
        article = Article.objects.get(id=article_id)
        article.delete()
        message = "Artykuł został usunięty."
        return redirect(f"/person_details/{person_id}")


class AcceptArticlePersonView(StaffMemberCheck, View):
    def get(self, request, person_id, article_id):
        person = Person.objects.get(id=person_id)
        article = Article.objects.get(id=article_id)
        ctx = {
            "person": person,
            "article": article
        }
        return render(request, "accept_article_person.html", ctx)
    
    def post(self, request, person_id, article_id):
        article = Article.objects.get(id=article_id)
        article.is_accepted = True
        article.save()
        message = "Artykuł został zaakceptowany."
        return redirect(f"/person_details/{person_id}")


class AddArticleMovieView(ActivateUserCheck, View):
    def get(self, request, id):
        user = User.objects.get(pk=int(request.session.get("user_id")))
        movie = Movie.objects.get(id=id)
        waiting_articles = [i for i in Article.objects.filter(article_added_by=user, is_accepted=False)]
        if user.is_staff or 3 > len(waiting_articles):
            form = AddArticleForm()
            ctx = {
                "movie": movie,
                "form": form
            }
            return render(request, "add_article_movie.html", ctx)
        return redirect("/movies")
    
    def post(self, request, id):
        form = AddArticleForm(request.POST)
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        error_message = "Coś poszło nie tak"
        message = None
        if form.is_valid():
            data = form.cleaned_data
            links = [i.link for i in Article.objects.all()]
            if data["url"] in links:
                error_message = "Taki link jest już w naszym archiwum."
                ctx = {
                    "form": form,
                    "movie": movie,
                    "error_message": error_message
                }
                return render(request, "add_article_movie.html", ctx)
            if user.is_staff:
                article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"], is_accepted=True)
                movie.movie_article.add(article)
                movie.save()
                message = "Artykuł dodany pomyślnie."
            else:
                article = Article.objects.create(article_name=data["name"], author=data["author"], article_added_by=user, link=data["url"])
                movie.movie_article.add(article)
                movie.save()
                message = "Artykuł czeka na akceptację."
            ctx = {
                "form": form,
                "movie": movie,
                "message": message
            }
            return render(request, "add_article_movie.html", ctx)
        ctx = {
            "form": form,
            "movie": movie,
            "error_message": error_message
        }
        return render(request, "add_article_movie.html", ctx)


class DeleteArticleMovieView(ActivateUserCheck, View):
    def get(self, request, movie_id, article_id):
        movie = Movie.objects.get(id=movie_id)
        article = Article.objects.get(id=article_id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if user.is_superuser or user.is_staff and not article.is_accepted or article.article_added_by == user and not movie.movie_edited_by or article.article_added_by == user and movie.movie_edited_by == user:
            ctx = {
                "movie": movie,
                "article": article
            }
            return render(request, "delete_article_movie.html", ctx)
        return redirect("/movies")
    
    def post(self, request, movie_id, article_id):
        article = Article.objects.get(id=article_id)
        article.delete()
        message = "Artykuł został usunięty."
        return redirect(f"/movie_details/{movie_id}")


class AcceptArticleMovieView(StaffMemberCheck, View):
    def get(self, request, movie_id, article_id):
        movie = Movie.objects.get(id=movie_id)
        article = Article.objects.get(id=article_id)
        ctx = {
            "movie": movie,
            "article": article
        }
        return render(request, "accept_article_movie.html", ctx)
    
    def post(self, request, movie_id, article_id):
        article = Article.objects.get(id=article_id)
        article.is_accepted = True
        article.save()
        message = "Artykuł został zaakceptowany."
        return redirect(f"/movie_details/{movie_id}")


class AddActorMovieView(ActivateUserCheck, View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if (movie.movie_added_by == user and movie.movie_edited_by == None) or (movie.movie_added_by == user and not movie.movie_edited_by.is_staff) or user.is_superuser or user.is_staff:
            form = AddActorForm()
            ctx = {
                "movie": movie,
                "form": form
            }
            return render(request, "add_actor_movie.html", ctx)
        return redirect("/movies")
    
    def post(self, request, id):
        form = AddActorForm(request.POST)
        movie = Movie.objects.get(id=id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        message = "Coś poszło nie tak"
        if form.is_valid():
            data = form.cleaned_data
            starring = [i for i in movie.starring.all()]
            if data["actor"] in starring:
                message = "Taki aktor jest już przypisany do tego filmu."
                ctx = {
                    "form": form,
                    "movie": movie,
                    "message": message
                }
                return render(request, "add_actor_movie.html", ctx)
            personmovie = PersonMovie.objects.create(role=data["role"], persons=data["actor"], movies=movie, personmovie_added_by=user)
            movie.starring.add(personmovie.persons)
            movie.save()
            message = "Aktor dodany pomyślnie"
            ctx = {
                "form": form,
                "movie": movie,
                "personmovie": personmovie,
                "message": message
            }
            return redirect(f"/movie_details/{movie.id}")
        ctx = {
            "form": form,
            "movie": movie,
            "message": message
        }
        return render(request, "add_actor_movie.html", ctx)
    

class DeleteActorMovieView(ActivateUserCheck, View):
    def get(self, request, movie_id, person_id):
        user = User.objects.get(pk=int(request.session.get("user_id")))
        movie = Movie.objects.get(id=movie_id)
        person = Person.objects.get(id=person_id)
        personmovie = PersonMovie.objects.get(persons=person_id, movies=movie_id)
        if user.is_superuser or personmovie.personmovie_added_by == user or movie.movie_added_by == user and not movie.movie_edited_by.is_staff:
            ctx = {
                "movie": movie,
                "person": person
            }
            return render(request, "delete_actor_movie.html", ctx)
        return redirect("/movies")
    
    def post(self, request, movie_id, person_id):
        personmovie = PersonMovie.objects.get(persons=person_id, movies=movie_id)
        personmovie.delete()
        message = "Aktor został usunięty z filmu."
        return redirect(f"/movie_details/{movie_id}")


class AddWatchlistView(ActivateUserCheck, View):
    def get(self, request, movie_id):
        movie = Movie.objects.get(id=movie_id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if not user in movie.watchlist.all():
            movie.watchlist.add(user)
            movie.save()
        return redirect(f"/movie_details/{movie_id}")


class RemoveWatchlistView(ActivateUserCheck, View):
    def get(self, request, movie_id):
        movie = Movie.objects.get(id=movie_id)
        user = User.objects.get(pk=int(request.session.get("user_id")))
        if user in movie.watchlist.all():
            movie.watchlist.remove(user)
            movie.save()
        return redirect(f"/movie_details/{movie_id}")


class WatchlistView(ActivateUserCheck, View):
    def get(self, request):
        user = None
        if request.session.get("user_id"):
            user = User.objects.get(pk=int(request.session.get("user_id")))
        movies = Movie.objects.filter(movie_accepted_by__isnull=False, watchlist=user).order_by("year")
        my_people = Person.objects.filter(person_added_by=user, person_accepted_by__isnull=False)
        my_genres = Genre.objects.filter(genre_added_by=user, genre_accepted_by__isnull=False)
        my_movies = Movie.objects.filter(movie_added_by=user, movie_accepted_by__isnull=False)
        rated_movies = MovieRating.objects.filter(user=user)
        rated_people = PersonRating.objects.filter(user=user)

        paginator = Paginator(movies, 10)
        page = request.GET.get("page")
        movies = paginator.get_page(page)

        ctx = {
            "movies": movies,
            "my_people": my_people,
            "my_genres": my_genres,
            "my_movies": my_movies,
            "rated_movies": rated_movies,
            "rated_people": rated_people
        }
        return render(request, "watchlist.html", ctx)


class SoldiersView(StaffMemberCheck, View):
    def get(self, request):
        soldiers = [i for i in User.objects.filter(userrank__isnull=False).order_by("-userrank__rank__id", "username") if i.username not in ("west", "westerny", "Andrzej Bakuła")]

        paginator = Paginator(soldiers, 10)
        page = request.GET.get("page")
        soldiers = paginator.get_page(page)

        ctx = {
            "soldiers": soldiers
        }
        return render(request, "soldiers.html", ctx)

