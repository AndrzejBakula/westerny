from django.db import models
from django.contrib.auth.models import User, AbstractUser
from datetime import timezone, date, timedelta


RANKS = (
    (1, "kawalerzysta"),
    (2, "kapral"),
    (3, "sierżant"),
    (4, "porucznik"),
    (5, "kapitan"),
    (6, "major"),
    (7, "pułkownik"),
    (8, "generał")
)

class Rank(models.Model):
    name = models.CharField(max_length=32, unique=True, choices=RANKS)


class Person(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    person_rating = models.FloatField(null=True, max_length=4)
    person_image = models.ImageField(blank=True, null=True, upload_to="person_images/")
    person_description = models.TextField(null=True, max_length=1500)
    person_added_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="person_added")
    person_accepted_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="person_accepted")
    person_edited_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="person_edited")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=64, unique=True)
    genre_image = models.ImageField(blank=True, null=True, upload_to="genre_images/")
    genre_description = models.TextField(null=True, max_length=1500)
    genre_added_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="genre_added")
    genre_accepted_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="genre_accepted")
    genre_edited_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="genre_edited")

    def __str__(self):
        return self.name


class Year(models.Model):
    year = models.IntegerField(null=False, unique=True)


class Movie(models.Model):
    title = models.CharField(max_length=128)
    director = models.ManyToManyField(Person, related_name='director')
    screenplay = models.ManyToManyField(Person, related_name='screenplay')
    music = models.ManyToManyField(Person, related_name='music')
    starring = models.ManyToManyField(Person, through="PersonMovie")
    year = models.ForeignKey(Year, null=False, on_delete=models.DO_NOTHING)
    movie_rating = models.FloatField(null=True, max_length=4)
    genre = models.ManyToManyField(Genre)
    movie_image = models.ImageField(blank=True, null=True, upload_to="movie_images/")
    movie_description = models.TextField(null=True, max_length=1500)
    movie_added_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="movie_added")
    movie_accepted_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="movie_accepted")
    movie_edited_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="movie_edited")


class PersonMovie(models.Model):
    role = models.CharField(max_length=128, null=True)
    role_rating = models.FloatField(null=True, max_length=4)
    persons = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    movies = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)


