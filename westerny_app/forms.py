from django import forms
# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV3
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from .models import Person, Genre


class AddMovieForm(forms.Form):
    title = forms.CharField(label="Nazwa", max_length=128, widget=forms.TextInput(attrs={"size": 40}))
    director = forms.ModelMultipleChoiceField(label="Reżyser", queryset=Person.objects.all())
    screenplay = forms.ModelMultipleChoiceField(label="Scenariusz", queryset=Person.objects.all())
    year = forms.CharField(label="Rok", max_length=4)
    genre = forms.ModelMultipleChoiceField(label="Gatunek", queryset=Genre.objects.all())
    image = forms.ImageField(label="Obraz", required=None)
    description = forms.CharField(label="Opis filmu", required=None, widget=forms.Textarea(attrs={"rows": 6, "cols": 40}))


