# Generated by Django 3.0.2 on 2020-02-10 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sky',
            name='year',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
