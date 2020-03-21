from django.db import models
from django.contrib.auth.models import User

#extends User model, user_type can be Shipper, Trucker or Driver
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=30)
    company_name = models.CharField(max_length=30)
