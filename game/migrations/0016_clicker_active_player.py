# Generated by Django 4.2 on 2023-04-23 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0015_clicker_delete_scrapeddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='clicker',
            name='active_player',
            field=models.IntegerField(default=0),
        ),
    ]