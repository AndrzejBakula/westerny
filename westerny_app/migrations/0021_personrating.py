# Generated by Django 3.1.2 on 2021-01-13 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('westerny_app', '0020_auto_20210113_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='westerny_app.person')),
                ('rating', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='westerny_app.rating')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
