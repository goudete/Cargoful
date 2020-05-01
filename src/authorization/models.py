from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

#extends User model, user_type can be Shipper, Trucker or Driver
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(_('User Type'), max_length=30)
    company_name = models.CharField(_('Company Name'), max_length=30)
    phone = PhoneNumberField(_('Phone'), unique=True)
    is_approved = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default = False)

class User_Feedback(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
