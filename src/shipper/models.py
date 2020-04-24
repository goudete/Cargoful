from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from trucker.models import truck_company, driver
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

"""this is the shipper model, a shipper has cargo that they need delivered"""
class shipper(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    active_orders = models.PositiveIntegerField(default = 0)
    total_orders = models.PositiveIntegerField(default = 0)
    cancelled_orders = models.PositiveIntegerField(default = 0)
    rating = models.PositiveIntegerField(default = 0, validators = [MaxValueValidator(5)])

"""with the @receiver decorator, we can link a signal with a function. This is what is used
to update shipper model data when a shipper registers"""
@receiver(post_save, sender=User)
def update_shipper_signal(sender, instance, created, **kwargs):
    if created:
        shipper.objects.create(user=instance)
    instance.shipper.save()

""" this is the order model, an order is a shipment"""
class order(models.Model):
    #this method is for getting the path to a picture of a carta porte document
    def get_carta_porte_path(file):
        return os.path.join('carta_porte', file)
    #this method is for geting the path to a picture of an orden de embarco document
    def get_orden_de_embarco(file):
        return os.path.join('orden_de_embarco', file)
    #fields
    is_approved = models.BooleanField(default = False)
    customer_order_no = models.CharField(default = '', max_length = 50) #this is for display on customer dashboard, format is 'cf<user_id><number>'
    shipping_company = models.ForeignKey(shipper, on_delete = models.PROTECT)
    truck_company = models.ForeignKey(truck_company, null=True, on_delete = models.CASCADE)
    driver = models.ForeignKey(driver, null = True, on_delete = models.SET_NULL)
    #geocode and address info
    pickup_latitude = models.DecimalField(default = 0.0, max_digits = 9, decimal_places = 6)
    pickup_longitude = models.DecimalField(default = 0.0, max_digits = 9, decimal_places = 6)
    delivery_latitude = models.DecimalField(default = 0.0, max_digits = 9, decimal_places = 6)
    delivery_longitude = models.DecimalField(default = 0.0, max_digits = 9, decimal_places = 6)
    pickup_address = models.TextField(default = "")
    delivery_address = models.TextField(default = "")
    #date info
    pickup_date = models.DateField(default = date.today, auto_now_add = False)
    delivery_date = models.DateField(default = date.today, auto_now_add = False)
    #other specs
    price = models.DecimalField(default = 0.0, max_digits = 9, decimal_places = 2, validators=[MinValueValidator(0.0)])
    distance = models.DecimalField(default = 0.0, max_digits = 15, decimal_places = 2)
    carta_porte = models.ImageField(upload_to = get_carta_porte_path, blank = True, null = True)
    orden_de_embarco = models.ImageField(upload_to = get_orden_de_embarco, blank = True, null = True)
    shipment_number = models.PositiveIntegerField(default = 0)
    numero_de_pedido = models.PositiveIntegerField(default = 0)
    numero_de_abaran = models.PositiveIntegerField(default = 0)
    pickup_time = models.TimeField(default = timezone.now, auto_now_add = False)
    delivery_time = models.TimeField(default = timezone.now, auto_now_add = False)
    contents = models.TextField(default = '')
    instructions = models.TextField(default = '')
    created_at = models.DateTimeField(auto_now_add=True)
    #truck_type is an option field, the user can pick one of the following options
    TRUCK_TYPES = [
        ('Low Boy', 'Low Boy'),
        ('Caja Seca 48 pies', 'Caja Seca 48 pies'),
        ('Refrigerado 48 pies', 'Refrigerado 48 pies'),
        ('Plataforma 48 pies', 'Plataforma 48 pies'),
        ('Caja Seca 53 pies', 'Caja Seca 53 pies'),
        ('Refrigerado 53 pies', 'Refrigerado 53 pies'),
        ('Plataforma 53 pies', 'Plataforma 53 pies'),
        ('Full Caja Seca', 'Full Caja Seca'),
        ('Full Refrigerado','Full Refrigerado'),
        ('Full Plataforma', 'Full Plataforma'),
        ('Torton Caja Seca', 'Torton Caja Seca'),
        ('Torton Refrigerado', 'Torton Refrigerado'),
        ('Torton Plataforma', 'Torton Plataforma'),
        ('Rabon Caja Seca', 'Rabon Caja Seca'),
        ('Rabon Refrigerado', 'Rabon Refrigerado'),
        ('Rabon Plataforma', 'Rabon Plataforma'),
        ('Camioneta 5.5 tons Seca', 'Camioneta 5.5 tons Seca'),
        ('Camioneta 5.5 tons Refrigerada','Camioneta 5.5 tons Refrigerada'),
        ('Camioneta 5.5 tons Plataforma','Camioneta 5.5 tons Plataforma'),
        ('Camioneta 3.5 tons Seca', 'Camioneta 3.5 tons Seca'),
        ('Camioneta 3.5 tons Refrigerada','Camioneta 3.5 tons Refrigerada'),
        ('Camioneta 3.5 tons Redila', 'Camioneta 3.5 tons Redila'),
        ('Camioneta 1.5 tons Seca', 'Camioneta 1.5 tons Seca'),
        ('Camioneta 1.5 tons Refrigerada', 'Camioneta 1.5 tons Refrigerada'),
        ('Camioneta 1.5 tons Redila','Camioneta 1.5 tons Redila')
    ]
    #create actual field
    truck_type = models.CharField(
        max_length = 40,
        choices = TRUCK_TYPES, #references above list object
        default = 'LB'
        )
    #status has 4 options
    status = models.PositiveIntegerField(default = 0, validators = [MaxValueValidator(5)])
    """for the status field:
    0 -> pending approval
    1 -> unassigned
    2 -> booked
    3 -> in transit
    4 -> delivered
    5 -> cancelled
    """

#this model is only for when a trucker updates the status of an order
class status_update(models.Model):
    trucker = models.ForeignKey(truck_company, on_delete = models.CASCADE) #the trucker that updated the order
    shipper = models.ForeignKey(shipper, on_delete = models.CASCADE) #the shipper whose order is being updated
    old_status = models.PositiveIntegerField(default = 0, validators = [MaxValueValidator(5)]) #the previous status of order
    new_status = models.PositiveIntegerField(default = 0, validators = [MaxValueValidator(5)]) #the updated status of order
    order = models.ForeignKey(order, on_delete = models.CASCADE) #the order associated w/ this status update
    date_time_changed = models.DateTimeField(auto_now_add = True, blank = True) #the date and time it was updated
    read = models.BooleanField(default = False) #if this is false, then it shows up in notifications, if its teue it does not

#this model is for when a shipper posts a new order, truckers connected with that shipper are notified
class order_post_notification(models.Model):
    order = models.ForeignKey(order, on_delete = models.CASCADE) #order associated w/ notification
    truckers = models.ManyToManyField(User) #truckers that can see this notification
