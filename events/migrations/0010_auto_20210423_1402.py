# Generated by Django 3.1.7 on 2021-04-23 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20210422_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='year',
            field=models.IntegerField(choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)], default=2),
        ),
    ]
