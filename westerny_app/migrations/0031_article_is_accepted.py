# Generated by Django 3.1.2 on 2021-02-03 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0030_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
    ]