# Generated by Django 3.1.7 on 2021-04-25 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_auto_20210423_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='year',
            field=models.IntegerField(choices=[(1, 'first'), (2, 'second'), (3, 'third'), (4, 'fourth')], default=2),
        ),
    ]
