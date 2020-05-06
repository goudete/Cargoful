from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from shipper.models import shipper
from .models import Profile
from django.utils.translation import gettext_lazy as _


class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta():
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
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



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('user_type', 'company_name', 'phone', 'company_type')
        USER_TYPES = (("Shipper", _("Shipper")), ("Trucker", _("Trucker")))
        COMPANY_TYPES = [('Persona Moral', _('Persona Moral')), ('Persona Física', _('Persona Física'))]
        widgets = {'user_type': forms.Select(choices=USER_TYPES), 'company_type': forms.Select(choices = COMPANY_TYPES)}
        help_texts = {
            'phone': 'formato: +525566290550'
        }
        error_messages = {
            'phone': {
                'unique': 'This number is already registered, please enter a new one'
            }
        }
