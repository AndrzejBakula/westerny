from django import forms
# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV3
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from .models import Person, Genre


class AddMovieForm(forms.Form):
    title = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Tytuł westernu"}))
    director = forms.ModelMultipleChoiceField(label="Reżyser", queryset=Person.objects.all())
    screenplay = forms.ModelMultipleChoiceField(label="Scenariusz", queryset=Person.objects.all())
    year = forms.CharField(label="", max_length=4, widget=forms.TextInput(attrs={"placeholder": "Rok produkcji"}))
    genre = forms.ModelMultipleChoiceField(label="Gatunek", queryset=Genre.objects.all())
    image = forms.ImageField(label="Dodaj obraz", required=None)
    description = forms.CharField(label="", required=None, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis"}))


class AddGenreForm(forms.Form):
    name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwa gatunku"}))
    description = forms.CharField(label="", required=None, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)


class EditGenreForm(forms.Form):
    name = forms.CharField(label="Nazwa", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwa gatunku"}))
    description = forms.CharField(label="", required=None, widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "placeholder": "Krótki opis"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)
    delete_image = forms.BooleanField(label="Skasować istniejący obraz?", required=None)


class AddPersonForm(forms.Form):
    first_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Imię"}))
    last_name = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwisko"}))
    image = forms.ImageField(label="Dodaj obraz", required=None)


class RegisterForm(forms.Form):
    username = forms.CharField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "Nazwa użytkownika"}))
    email = forms.EmailField(label="", max_length=128, widget=forms.TextInput(attrs={"size": 38, "placeholder": "adres email"}))
    password = forms.CharField(label="", widget=forms.PasswordInput({"size": 38, "placeholder": "hasło"},))
    password2 = forms.CharField(label="", widget=forms.PasswordInput({"size": 38, "placeholder": "powtórz hasło"},))