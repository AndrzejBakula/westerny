# Generated by Django 3.1.2 on 2021-02-02 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('westerny_app', '0029_auto_20210128_1908'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.IntegerField()),
            ],
        ),
    ]
