# Generated by Django 3.0.4 on 2020-04-12 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]