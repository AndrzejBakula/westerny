# Generated by Django 3.1.2 on 2021-01-04 20:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('westerny_app', '0009_auto_20210104_1926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='genre',
            old_name='genre_added',
            new_name='genre_added_by',
        ),
        migrations.RenameField(
            model_name='genre',
            old_name='genre_edited',
            new_name='genre_edited_by',
        ),
        migrations.RenameField(
            model_name='movie',
            old_name='movie_added',
            new_name='movie_added_by',
        ),
        migrations.RenameField(
            model_name='movie',
            old_name='movie_edited',
            new_name='movie_edited_by',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='person_added',
            new_name='person_added_by',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='person_edited',
            new_name='person_edited_by',
        ),
        migrations.AddField(
            model_name='genre',
            name='genre_accepted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='genre_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_accepted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='movie_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='person',
            name='person_accepted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='genre',
            name='genre_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='movie',
            name='movie_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='person',
            name='person_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
