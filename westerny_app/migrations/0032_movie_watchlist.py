# Generated by Django 3.1.2 on 2021-02-13 17:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('westerny_app', '0031_article_is_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='watchlist',
            field=models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL),
        ),
    ]
