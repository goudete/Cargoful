from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from shipper.models import shipper
from .models import Profile
from django.utils.translation import gettext_lazy as _


class CreateUserForm(UserCreationForm):
    class Meta():
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }
        labels = {
            'username': None,
            'password1': None,
            'password2': None,
        }

        # def __init__(self, *args, **kwargs):
        #     super(UserCreateForm, self).__init__(*args, **kwargs)
        #     for fieldname in fields:
        #         self.fields[fieldname].help_texts = None



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user_type', 'company_name', 'phone',)
        USER_TYPES = (("Shipper", _("Shipper")), ("Trucker", _("Trucker")))
        widgets = {'user_type': forms.Select(choices=USER_TYPES)}
        error_messages = {
            'phone': {
                'unique': 'This number is already registered, please enter a new one'
            }
        }
