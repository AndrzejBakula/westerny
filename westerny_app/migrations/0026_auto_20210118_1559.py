# Generated by Django 3.1.2 on 2021-01-18 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0025_movie_cinema'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='date_birth',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='date_death',
            field=models.DateField(default=None, null=True),
        ),
    ]