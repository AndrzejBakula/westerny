from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from .models import Product, Category, Client
from .models import default_timedelta


class AddMovieForm(forms.Form):
    title = forms.CharField(label="Nazwa", max_length=128)
    director = forms.ModelChoiceField(label="Reżyser", queryset=Person.objects.all(), widget=forms.ModelMultipleChoiceField)
    screenplay = forms.ModelChoiceField(label="Scenariusz", queryset=Person.objects.all(), widget=forms.ModelMultipleChoiceField)
    year = forms.CharField(label="Rok", max_length=4)
    genre = forms.ModelMultipleChoiceField(label="Gatunek", queryset=Genre.objects.all(), widget=forms.ModelMultipleChoiceField)
    image = forms.ImageField(label="Obraz", required=None)
    description = forms.CharField(label="Opis filmu", required=None, widget=forms.Textarea(attrs={"rows": 5}))


