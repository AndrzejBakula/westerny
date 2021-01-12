# Generated by Django 3.1.2 on 2021-01-08 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0010_auto_20210104_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='genre_description',
            field=models.TextField(max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='movie_description',
            field=models.TextField(max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='person_description',
            field=models.TextField(max_length=1500, null=True),
        ),
    ]