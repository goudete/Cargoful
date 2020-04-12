from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class truck_company(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    # is_approved = models.BooleanField(default = False)
    number_of_active_orders = models.IntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    incomplete_orders = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])
    # USERNAME_FIELD = 'email'
    def _str_(self):
        return self.company_name
@receiver(post_save, sender=User)
def update_truck_company_signal(sender, instance, created, **kwargs):
    if created:
        truck_company.objects.create(user=instance)
    instance.truck_company.save()

class trucks(models.Model):
    truck_company = models.ForeignKey(truck_company, on_delete=models.CASCADE)
    driver = models.ForeignKey('driver', on_delete=models.CASCADE)
    licence_plate = models.CharField(max_length=15)
    model = models.CharField(max_length=30)
    #truck_type is an option field, the user can pick one of the following
    TRUCK_TYPES = [
        ('Low Boy', 'Low Boy'),
        ('Caja Seca 48 pies', 'Caja Seca 48 pies'),
        ('Refrigerado 48 pies', 'Refrigerado 48 pies'),
        ('Plataforma 48 pies', 'Plataforma 48 pies'),
        ('Caja Seca 53 pies', 'Caja Seca 53 pies'),
        ('Refrigerado 53 pies', 'Refrigerado 53 pies'),
        ('Plataforma 53 pies', 'Plataforma 53 pies'),
        ('Full', 'Full'),
        ('Plataforma Full', 'Plataforma Full'),
        ('Torton Caja Seca', 'Torton Caja Seca'),
        ('Torton Refrigerado', 'Torton Refrigerado'),
        ('Troton Plataforma', 'Troton Plataforma'),
        ('Rabon Caja Seca', 'Rabon Caja Seca'),
        ('Rabon Refrigerado', 'Rabon Refrigerado'),
        ('Rabon Plataforma', 'Rabon Plataforma'),
        ('Camioneta 5.5 tons', 'Camioneta 5.5 tons'),
        ('Camioneta 3.5 tons', 'Camioneta 3.5 tons'),
        ('Camioneta 3.5 tons Plataforma', 'Camioneta 3.5 tons Plataforma'),
        ('Camioneta 1.5 tons', 'Camioneta 1.5 tons'),
        ('Camioneta 3.5 tons Redilla', 'Camioneta 3.5 tons Redilla'),
    ]
    #create actual field
    truck_type = models.CharField(
        max_length = 40,
        choices = TRUCK_TYPES,
        default = 'LB'
        )
    year = models.PositiveIntegerField(default=0)
    available_capacity = models.PositiveIntegerField(default=0)

    def _str_(self):
        return self.licence_plate

class driver(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    is_approved = models.BooleanField(default = False)
    truck_company = models.ForeignKey(truck_company, on_delete=models.CASCADE)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=50)
    orders_completed = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])

    def _str_(self):
        return self.fname
