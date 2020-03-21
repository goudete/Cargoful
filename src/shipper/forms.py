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
# class Order_Form(forms.ModelForm):
#     pickup_latitude = forms.DecimalField(widget=forms.NumberInput(
#         attrs={
#             'class': 'form-control',
#             'placeholder': 'Pickup Latitude...'
#         }
#     ), label='')
#     pickup_longitude = forms.DecimalField(widget=forms.NumberInput(
#         attrs={
#             'class': 'form-control',
#             'placeholder': 'Pickup Longitude...'
#         }
#     ), label='')
#     delivery_latitude = forms.DecimalField(widget=forms.NumberInput(
#         attrs={
#             'class': 'form-control',
#             'placeholder': 'Delivery Latitude...'
#         }
#     ), label='')
#     delivery_longitude = forms.DecimalField(widget=forms.NumberInput(
#         attrs={
#             'class': 'form-control',
#             'placeholder': 'Delivery Longitude...'
#         }
#     ), label='')
#     pickup_date = forms.DateField()
#     # pickup_date = forms.DateField(widget=forms.SelectDateWidget(
#     #     attrs={
#     #         'class': 'input'
#     #     }
#     # ), label='')
#
#     class Meta:
#         model = order
#         fields = ['pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude', 'pickup_date']

    #helper = FormHelper()
    #helper.form_method = 'POST'
    #helper.layout = Layout()
    #.add_input(Submit('login', 'login', css_class='btn-primary'))
    # class NewOrderWidget(forms.NumberInput):
    #     class Media:
    #         css = {
    #             'all': ('style.css')
    #         }
            #js
