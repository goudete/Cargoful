from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from shipper.models import shipper
from .models import Profile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django import forms
from crispy_forms.helper import FormHelper

class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email_passed = self.cleaned_data.get('email')
        if User.objects.filter(email=email_passed).exists():
            raise forms.ValidationError("User with that email already exists")
        return email_passed

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
class EditUserInfo(forms.Form):
    first_name = forms.CharField(max_length=100, required = False)
    last_name = forms.CharField(max_length=100, required = False)
    email = forms.EmailField(required = False)
    company_name = forms.CharField(max_length=100, required = False)
    username = forms.CharField(max_length=100, required = False)

    def __init__(self, *args, **kwargs):
        super(EditUserInfo, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields['company_name'].disabled = True
        self.fields['username'].disabled = True


class PasswordChangeFormCustom(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeFormCustom, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

class SettingsForm(forms.Form):
    order_email_notifications = forms.BooleanField()
