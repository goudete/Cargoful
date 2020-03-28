from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from shipper.models import shipper
from .models import Profile


class CreateUserForm(UserCreationForm):
    class Meta():
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user_type', 'company_name')
        USER_TYPES = (("Shipper", "Shipper"),("Trucker", "Trucker"),("Driver", "Driver"))
        widgets = {'user_type': forms.Select(choices=USER_TYPES)}
