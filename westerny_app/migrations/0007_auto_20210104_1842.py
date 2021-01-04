# Generated by Django 3.1.2 on 2021-01-04 18:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('westerny_app', '0006_auto_20210104_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genre',
            name='who_added',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='who_added',
        ),
        migrations.RemoveField(
            model_name='person',
            name='who_added',
        ),
        migrations.AddField(
            model_name='genre',
            name='genre_accepted',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='genre_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='genre',
            name='genre_added',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='genre_added', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='genre',
            name='genre_edited',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='genre_edited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_accepted',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='movie_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_added',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='movie_added', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movie',
            name='movie_edited',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='movie_edited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='person',
            name='person_accepted',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person_accepted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='person',
            name='person_added',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person_added', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='person',
            name='person_edited',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person_edited', to=settings.AUTH_USER_MODEL),
        ),
    ]
