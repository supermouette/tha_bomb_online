# Generated by Django 3.0.5 on 2020-05-02 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20200412_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='order_in_hand',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]