# Generated by Django 3.1.2 on 2021-01-10 20:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0013_auto_20210110_1359'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='article_adde_by',
            new_name='article_added_by',
        ),
    ]
