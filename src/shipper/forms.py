from django import forms
from .models import order, WeeklyRecurringOrder
from crispy_forms.helper import FormHelper
from datetime import datetime
from django.contrib.admin.widgets import AdminDateWidget


class Order_Form(forms.ModelForm):
    class Meta:
        model = order
        fields = [
            'pickup_date',
            'pickup_time',
            'truck_type',
            'price',
            'weight',
            'contents',
            'instructions'
            ]
        widgets = {
            'pickup_date': forms.DateInput(attrs={'id':'datepicker', 'class': 'require-if-active', 'data-require-pair': '#include_date'}),
            'pickup_time': forms.TimeInput(attrs = {'id': 'timepicker', 'class': 'require-if-active', 'data-require-pair': '#include_time'}),
            'instructions': forms.Textarea(attrs={'cols': 5, 'rows': 5})
        }
    def __init__(self, *args, **kwargs):
        super(Order_Form, self).__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['min'] = 0

class WeeklyRecurrenceForm(Order_Form):
    class Meta(Order_Form.Meta):
        model = WeeklyRecurringOrder
        fields = Order_Form.Meta.fields + ['number_of_weeks','weekdays','end_opt','start_day','end_by_day']#,'occurrences']
    def __init__(self, *args, **kwargs):
        super(WeeklyRecurrenceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
