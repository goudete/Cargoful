from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

#extends User model, user_type can be Shipper, Trucker or Driver
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=30)
    company_name = models.CharField(max_length=30)
    phone = PhoneNumberField(unique=True)
    is_approved = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)

class User_Feedback(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
