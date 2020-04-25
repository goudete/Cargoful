"""This file contains all the tedious code needed to move the data
for recurring orders through the posting/confirmation process.
Here so it doesnt clutter up rest of code ;)"""
from .forms import WeeklyRecurrenceForm
from .models import shipper, order, WeeklyRecurringOrder
import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect


def getRecurrenceVars(recurrence_type,request,jsn):
    recurrence_vars = {}
    if recurrence_type == 'Daily':
        recurrence_vars['recurrence_type'] = recurrence_type
        dayopt = request.POST.get("day_type_opts", None)
        if dayopt == 'option1':
            every_x_days = jsn['number_of_days']
            recurrence_vars['option'] = dayopt
            recurrence_vars['every_x_days'] = every_x_days
        else:
            recurrence_vars['option'] = dayopt
    elif recurrence_type == 'Weekly':
        recurrence_vars['recurrence_type'] = recurrence_type
        every_x_weeks = jsn['number_of_weeks']
        recurrence_vars['number_of_weeks'] = every_x_weeks
        weekdays = ""
        for day in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
            if day + "Check" in jsn:
                weekdays += "1"
            else:
                weekdays += "0"
        recurrence_vars['weekdays'] = weekdays
    elif recurrence_type == 'Monthly':
        recurrence_vars['recurrence_type'] = recurrence_type
        monthopt = request.POST.get("month_opts", None)
        if monthopt == 'option1':
            every_x_months = jsn['number_of_months']
            day_of_month = jsn['day_of_month']
            recurrence_vars['every_x_months'] = every_x_months
            recurrence_vars['day_of_month'] = day_of_month
            recurrence_vars['option'] = monthopt
        else:
            every_x_months = jsn['number_of_months2']
            day_select_month = jsn['day_select_month']
            weekday_select_month = jsn['weekday_select_month']
            recurrence_vars['every_x_months'] = every_x_months
            recurrence_vars['day_select_month'] = day_select_month
            recurrence_vars['weekday_select_month'] = weekday_select_month
            recurrence_vars['option'] = monthopt
    elif recurrence_type == 'Yearly':
        recurrence_vars['recurrence_type'] = recurrence_type
        year_opt = request.POST.get("year_opts", None)
        if year_opt == 'option1':
            day_of_month_year = jsn['day_of_month_year']
            month_select = jsn['month_select']
            recurrence_vars['day_of_month_year'] = day_of_month_year
            recurrence_vars['month'] = month
            recurrence_vars['option'] = year_opt
        else:
            day_select_year = jsn['day_select_year']
            weekday_select_year = jsn['weekday_select_year']
            month_select2 = jsn['month_select2']
            recurrence_vars['day_select_year'] = day_select_year
            recurrence_vars['month_select2'] = month_select2
            recurrence_vars['weekday_select_year'] = weekday_select_year
            recurrence_vars['option'] = year_opt

    return recurrence_vars

def getRecurrenceEndVars(recurrence_type,request,jsn):
    recurrence_end_vars = {}
    start_day = jsn['start_day']
    end_opt = request.POST.get("end_opts", None)
    recurrence_end_vars['start_day'] = start_day
    recurrence_end_vars['end_opt'] = end_opt
    if end_opt == 'option1':
        end_by_day = jsn['end_by_day']
        recurrence_end_vars['end_by_day'] = end_by_day
    elif end_opt == 'option2':
        recurrence_end_vars['occurrences'] = jsn['occurrences']
    else:
        pass
    return recurrence_end_vars

def getRecurrenceVarsFromConfirmation(recurrence_type,jsn):
    recurrence_vars = {}
    recurrence_vars['recurrence_indicator'] = jsn['recurrence_indicator']
    if recurrence_type == 'Daily':
        recurrence_vars['recurrence_type'] = recurrence_type
        dayopt = jsn['option']
        if dayopt == 'option1':
            every_x_days = jsn['number_of_days']
            recurrence_vars['option'] = dayopt
            recurrence_vars['every_x_days'] = every_x_days
        else:
            recurrence_vars['option'] = dayopt
    elif recurrence_type == 'Weekly':
        recurrence_vars['recurrence_type'] = recurrence_type
        every_x_weeks = jsn['number_of_weeks']
        recurrence_vars['number_of_weeks'] = every_x_weeks
        weekdays = jsn['weekdays']
        recurrence_vars['weekdays'] = weekdays
    elif recurrence_type == 'Monthly':
        recurrence_vars['recurrence_type'] = recurrence_type
        monthopt = jsn['option']
        if monthopt == 'option1':
            every_x_months = jsn['number_of_months']
            day_of_month = jsn['day_of_month']
            recurrence_vars['every_x_months'] = every_x_months
            recurrence_vars['day_of_month'] = day_of_month
            recurrence_vars['option'] = monthopt
        else:
            every_x_months = jsn['number_of_months2']
            day_select_month = jsn['day_select_month']
            weekday_select_month = jsn['weekday_select_month']
            recurrence_vars['every_x_months'] = every_x_months
            recurrence_vars['day_select_month'] = day_select_month
            recurrence_vars['weekday_select_month'] = weekday_select_month
            recurrence_vars['option'] = monthopt
    elif recurrence_type == 'Yearly':
        recurrence_vars['recurrence_type'] = recurrence_type
        year_opt = jsn['option']
        if year_opt == 'option1':
            day_of_month_year = jsn['day_of_month_year']
            month_select = jsn['month_select']
            recurrence_vars['day_of_month_year'] = day_of_month_year
            recurrence_vars['month'] = month
            recurrence_vars['option'] = year_opt
        else:
            day_select_year = jsn['day_select_year']
            weekday_select_year = jsn['weekday_select_year']
            month_select2 = jsn['month_select2']
            recurrence_vars['day_select_year'] = day_select_year
            recurrence_vars['month_select2'] = month_select2
            recurrence_vars['weekday_select_year'] = weekday_select_year
            recurrence_vars['option'] = year_opt

    return recurrence_vars

def getRecurrenceEndVarsFromConfirmation(recurrence_type,jsn):
    recurrence_end_vars = {}
    start_day = jsn['start_day']
    end_opt = jsn['end_opt']
    recurrence_end_vars['start_day'] = start_day
    recurrence_end_vars['end_opt'] = end_opt
    if end_opt == 'option1':
        end_by_day = jsn['end_by_day']
        recurrence_end_vars['end_by_day'] = end_by_day
    elif end_opt == 'option2':
        recurrence_end_vars['occurrences'] = jsn['occurrences']
    else:
        pass
    return recurrence_end_vars

def saveWeeklyRecurringOrder(recurrence_vars,recurrence_end_vars,request):
    print("TRYNNA SAVE ORDER")
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    #geocode stuff
    pu_lat, pu_long = jsn['pickup_latitude'], jsn['pickup_longitude']
    del_lat, del_long = jsn['delivery_latitude'], jsn['delivery_longitude']
    #address stuff
    pu_address, del_address = jsn['pickup_address'], jsn['delivery_address']
    #distance
    dist = float(jsn['distance'])
    #create the customer_order_no field
    id = request.user.id
    ship = shipper.objects.filter(user = request.user).first()
    num_orders = len(order.objects.filter(shipping_company = ship))+1
    customer_order_no = 'CF'+str(id)+"-"+str(num_orders)

    n_order = WeeklyRecurrenceForm(request.POST)
    if n_order.is_valid():
        new_order = n_order.save(commit = False)
        company = shipper.objects.filter(user = request.user).first()
        new_order.customer_order_no = customer_order_no
        new_order.shipping_company = company
        new_order.pickup_latitude = pu_lat
        new_order.pickup_longitude = pu_long
        new_order.delivery_latitude = del_lat
        new_order.delivery_longitude = del_long
        new_order.pickup_address = pu_address
        new_order.delivery_address = del_address
        new_order.distance = round(dist,2)
        new_order.weekdays = recurrence_vars['weekdays']
        new_order.number_of_weeks = recurrence_vars['number_of_weeks']
        new_order.end_opt = recurrence_end_vars['end_opt']
        new_order.start_day = recurrence_end_vars['start_day']
        if recurrence_end_vars['end_opt'] == 'option1':
            new_order.end_by_day = recurrence_end_vars['end_by_day']
        elif recurrence_end_vars['end_opt'] == 'option2':
            new_order.occurrences = recurrence_end_vars['occurrences']
        else:
            new_order.indefinite = True
        new_order.save()
        messages.info(request, "Order "+ str(customer_order_no) + " Placed Successfully")
        return HttpResponseRedirect('/shipper')
