from django.db import models
from datetime import timezone, date, timedelta

class Person(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    person_image = models.ImageField(blank=True, null=True, upload_to="person_images/")
    who_added = models.CharField(max_length=64, default="Westerny")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=64)
    genre_image = models.ImageField(blank=True, null=True, upload_to="genre_images/")
    who_added = models.CharField(max_length=64, default="Westerny")
    genre_description = models.TextField(null=True, default="")

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=128)
    director = models.ManyToManyField(Person, related_name='director')
    screenplay = models.ManyToManyField(Person, related_name='screenplay')
    music = models.ManyToManyField(Person, related_name='music')
    starring = models.ManyToManyField(Person, through="PersonMovie")
    year = models.IntegerField(null=False)
    rating = models.FloatField(null=True)
    genre = models.ManyToManyField(Genre)
    movie_image = models.ImageField(blank=True, null=True, upload_to="movie_images/")
    description = models.TextField(null=True, default="")
    who_added = models.CharField(max_length=64, default="Westerny")


class PersonMovie(models.Model):
    role = models.CharField(max_length=128, null=True)
    persons = models.ForeignKey(Person, on_delete=models.CASCADE)
    movies = models.ForeignKey(Movie, on_delete=models.CASCADE)


