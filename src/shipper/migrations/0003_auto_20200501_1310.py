# Generated by Django 3.0.4 on 2020-05-01 20:10

import datetime
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0002_auto_20200424_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Weight'),
        ),
        migrations.AlterField(
            model_name='order',
            name='contents',
            field=models.TextField(default='', verbose_name='Contents'),
        ),
        migrations.AlterField(
            model_name='order',
            name='instructions',
            field=models.TextField(default='', verbose_name='Instructions'),
        ),
        migrations.AlterField(
            model_name='order',
            name='pickup_date',
            field=models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Pickup Date'),
        ),
        migrations.AlterField(
            model_name='order',
            name='pickup_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Pickup Time'),
        ),
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='order',
            name='truck_type',
            field=models.CharField(choices=[('Low Boy', 'Low Boy'), ('Caja Seca 48 pies', 'Caja Seca 48 pies'), ('Refrigerado 48 pies', 'Refrigerado 48 pies'), ('Plataforma 48 pies', 'Plataforma 48 pies'), ('Caja Seca 53 pies', 'Caja Seca 53 pies'), ('Refrigerado 53 pies', 'Refrigerado 53 pies'), ('Plataforma 53 pies', 'Plataforma 53 pies'), ('Full Caja Seca', 'Full Caja Seca'), ('Full Refrigerado', 'Full Refrigerado'), ('Full Plataforma', 'Full Plataforma'), ('Torton Caja Seca', 'Torton Caja Seca'), ('Torton Refrigerado', 'Torton Refrigerado'), ('Torton Plataforma', 'Torton Plataforma'), ('Rabon Caja Seca', 'Rabon Caja Seca'), ('Rabon Refrigerado', 'Rabon Refrigerado'), ('Rabon Plataforma', 'Rabon Plataforma'), ('Camioneta 5.5 tons Seca', 'Camioneta 5.5 tons Seca'), ('Camioneta 5.5 tons Refrigerada', 'Camioneta 5.5 tons Refrigerada'), ('Camioneta 5.5 tons Plataforma', 'Camioneta 5.5 tons Plataforma'), ('Camioneta 3.5 tons Seca', 'Camioneta 3.5 tons Seca'), ('Camioneta 3.5 tons Refrigerada', 'Camioneta 3.5 tons Refrigerada'), ('Camioneta 3.5 tons Redila', 'Camioneta 3.5 tons Redila'), ('Camioneta 1.5 tons Seca', 'Camioneta 1.5 tons Seca'), ('Camioneta 1.5 tons Refrigerada', 'Camioneta 1.5 tons Refrigerada'), ('Camioneta 1.5 tons Redila', 'Camioneta 1.5 tons Redila')], default='LB', max_length=40, verbose_name='Truck Type'),
        ),
    ]
