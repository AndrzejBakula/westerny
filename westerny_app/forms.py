from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from .models import Person, Genre, Rating, Movie, Year


class AddMovieForm(forms.Form):
    title = forms.CharField(label="", required=True, max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Tytuł nr 1"}))
    org_title = forms.CharField(label="", required=None, max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Ew. tytuł nr 2 (np. oryginalny)"}))
    year = forms.ModelChoiceField(label="Rok", required=True, queryset=Year.objects.all())
    director = forms.ModelMultipleChoiceField(label="Reżyser", required=True, queryset=Person.objects.all().order_by("last_name"))
    screenplay = forms.ModelMultipleChoiceField(label="Scenariusz", required=None, queryset=Person.objects.all().order_by("last_name"))
    music = forms.ModelMultipleChoiceField(label="Muzyka", required=None, queryset=Person.objects.all().order_by("last_name"))
    cinema = forms.ModelMultipleChoiceField(label="Zdjęcia", required=None, queryset=Person.objects.all().order_by("last_name"))
    genre = forms.ModelMultipleChoiceField(label="Gatunek", queryset=Genre.objects.all().order_by("name"))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków)"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)


class EditMovieForm(forms.Form):
    title = forms.CharField(label="", required=True, max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Tytuł westernu"}))
    org_title = forms.CharField(label="", required=None, max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Ew. tytuł nr 2 (np. oryginalny)"}))
    year = forms.ModelChoiceField(label="Rok", required=True, queryset=Year.objects.all())
    director = forms.ModelMultipleChoiceField(label="Reżyser", required=True, queryset=Person.objects.all().order_by("last_name"))
    screenplay = forms.ModelMultipleChoiceField(label="Scenariusz", required=None, queryset=Person.objects.all().order_by("last_name"))
    music = forms.ModelMultipleChoiceField(label="Muzyka", required=None, queryset=Person.objects.all().order_by("last_name"))
    cinema = forms.ModelMultipleChoiceField(label="Zdjęcia", required=None, queryset=Person.objects.all().order_by("last_name"))
    genre = forms.ModelMultipleChoiceField(label="Gatunek", queryset=Genre.objects.all().order_by("name"))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków)"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)
    delete_image = forms.BooleanField(label="Skasować istniejący obraz?", required=None)


class AddActorForm(forms.Form):
    actor = forms.ModelChoiceField(label="Aktor", required=True, queryset=Person.objects.all().order_by("last_name"))
    role = forms.CharField(label="", required=True, max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Rola w filmie"}))


class AddGenreForm(forms.Form):
    name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwa gatunku"}))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków)"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)


class EditGenreForm(forms.Form):
    name = forms.CharField(label="Nazwa", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwa gatunku"}))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)
    delete_image = forms.BooleanField(label="Skasować istniejący obraz?", required=None)


class AddPersonForm(forms.Form):
    first_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Imię"}))
    last_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwisko"}))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków)"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)
    date_birth = forms.CharField(label="Data urodzenia", widget=forms.TextInput(attrs={"type": "date"}))
    date_death = forms.CharField(label="Data śmierci", required=None, widget=forms.TextInput(attrs={"type": "date"}))


class EditPersonForm(forms.Form):
    first_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Imię"}))
    last_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwisko"}))
    description = forms.CharField(label="", max_length=1500, required=True, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis (do 1500 znaków)"}))
    date_birth = forms.CharField(label="Data urodzenia", widget=forms.TextInput(attrs={"type": "date"}))
    date_death = forms.CharField(label="Data śmierci", required=None, widget=forms.TextInput(attrs={"type": "date"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)
    delete_image = forms.BooleanField(label="Skasować istniejący obraz?", required=None)


class RegisterForm(forms.Form):
    username = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 34, "placeholder": "Nazwa kawalerzysty"}))
    email = forms.EmailField(label="", max_length=128, widget=forms.EmailInput(attrs={"size": 34, "placeholder": "Adres email"}))
    password = forms.CharField(label="", widget=forms.PasswordInput({"size": 34, "placeholder": "Hasło"},))
    password2 = forms.CharField(label="", widget=forms.PasswordInput({"size": 34, "placeholder": "Powtórz hasło"},))
    captcha = ReCaptchaField(label="", widget=ReCaptchaV3(attrs={'required_score':0.85}))


class LoginForm(forms.Form):
    username = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 34, "placeholder": "Nazwa kawalerzysty"}))
    password = forms.CharField(label="", widget=forms.PasswordInput({"size": 34, "placeholder": "Hasło"},))
    captcha = ReCaptchaField(label="", widget=ReCaptchaV3(attrs={'required_score':0.85}))


class SearchMovieForm(forms.Form):
    text = forms.CharField(label="", max_length=64, widget=forms.TextInput(attrs={"size": 34, "placeholder": "Wprowadź fragment tytułu" }))


class SearchPersonForm(forms.Form):
    text = forms.CharField(label="", max_length=64, widget=forms.TextInput(attrs={"size": 34, "placeholder": "Wprowadź fragment nazwiska" }))


class AddArticleForm(forms.Form):
    name = forms.CharField(label="", max_length=128, required=True, widget=forms.TextInput(attrs={"size": 40, "placeholder": "Nazwa artykułu"}))
    author = forms.CharField(label="", max_length=64, required=None, widget=forms.TextInput(attrs={"size": 34, "placeholder": "Autor lub nazwa witryny"}))
    url = forms.URLField(label="", required=True, widget=forms.TextInput(attrs={"size": 40, "placeholder": "tu skopiuj adres www"}))


class RatingForm(forms.Form):
    rating = forms.ModelChoiceField(label="Dodaj ocenę", queryset=Rating.objects.all())