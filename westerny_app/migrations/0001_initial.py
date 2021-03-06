# Generated by Django 3.1.2 on 2020-11-01 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('genre_image', models.ImageField(blank=True, null=True, upload_to='genre_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('year', models.IntegerField()),
                ('rating', models.FloatField(null=True)),
                ('movie_image', models.ImageField(blank=True, null=True, upload_to='movie_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('person_image', models.ImageField(blank=True, null=True, upload_to='person_images/')),
            ],
        ),
        migrations.CreateModel(
            name='PersonMovie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=128, null=True)),
                ('movies', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='westerny_app.movie')),
                ('persons', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='westerny_app.person')),
            ],
        ),
        migrations.AddField(
            model_name='movie',
            name='director',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='director', to='westerny_app.person'),
        ),
        migrations.AddField(
            model_name='movie',
            name='genre',
            field=models.ManyToManyField(to='westerny_app.Genre'),
        ),
        migrations.AddField(
            model_name='movie',
            name='screenplay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screenplay', to='westerny_app.person'),
        ),
        migrations.AddField(
            model_name='movie',
            name='starring',
            field=models.ManyToManyField(through='westerny_app.PersonMovie', to='westerny_app.Person'),
        ),
    ]
