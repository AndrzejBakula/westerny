# Generated by Django 3.1.2 on 2021-01-04 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0008_auto_20210104_1907'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='rating',
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_rating',
            field=models.FloatField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='person_rating',
            field=models.FloatField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='personmovie',
            name='role_rating',
            field=models.FloatField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='year',
            name='year',
            field=models.IntegerField(unique=True),
        ),
    ]
