# Generated by Django 3.0.4 on 2020-04-19 01:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trucker', '0006_auto_20200419_0035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='counter_offer',
            name='is_accepted',
        ),
        migrations.AddField(
            model_name='counter_offer',
            name='status',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(2)]),
        ),
    ]
