# Generated by Django 3.1.7 on 2021-04-27 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20210425_1759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='author',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='read',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='recipients',
        ),
    ]
