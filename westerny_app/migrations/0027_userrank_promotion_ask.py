# Generated by Django 3.1.2 on 2021-01-20 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0026_auto_20210118_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrank',
            name='promotion_ask',
            field=models.BooleanField(default=False),
        ),
    ]
