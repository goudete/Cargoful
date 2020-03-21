from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Profile

#On second save() in register_view, it adds user to respective Group.
#For reference: https://www.youtube.com/watch?v=jYzTKcvO0Pk&t=217s
#https://stackoverflow.com/questions/6288661/adding-a-user-to-a-group-in-django
def signal_profile(sender, instance, created, **kwargs):
    if created:
        usertype = instance.user_type
        group = Group.objects.get(name=usertype)
        group.user_set.add(instance.user)

post_save.connect(signal_profile, sender=Profile)
