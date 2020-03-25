from django import forms
from .models import order
from crispy_forms.helper import FormHelper


class Order_Form(forms.ModelForm):
    class Meta:
        model = order
        fields = [
            'pickup_date',
            'pickup_time',
            'truck_type',
            'price',
            'contents',
            'instructions'
            ]
