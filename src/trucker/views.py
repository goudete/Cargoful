from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from shipper.models import order, shipper
from trucker.models import truck_company, trucks, driver
from authorization.decorators import allowed_users
from rest_framework.decorators import api_view
import json
import math
from django.contrib import messages
# Create your views here.
@login_required
@allowed_users(allowed_roles=['Trucker'])
def Available_Orders(request):
    if request.method == 'GET':
        available = order.objects.filter(status__exact=0)
        return render(request, 'trucker/available_orders.html', {'available': available})


@login_required
@allowed_users(allowed_roles=['Trucker'])
def My_Orders(request):
    if request.method == 'GET':
        me = truck_company.objects.filter(user=request.user).first()
        my_orders = order.objects.filter(truck_company=me)
    return render(request, 'trucker/my_orders.html', {'my_orders': my_orders})


@login_required
@allowed_users(allowed_roles=['Trucker'])
@api_view(['POST'])
def Confirm_Order(request):
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
    order_id = jsn['order_id']
    #post to db and remove from available jobs
    # POST truck_company , status change to 1
    me = truck_company.objects.filter(user=request.user).first()
    cur_order = order.objects.filter(id=order_id).first()
    """calculate midpoint of lat and long for map in html page"""
    x,y,z = 0,0,0
    lat1,long1 = math.radians(cur_order.pickup_latitude), math.radians(cur_order.pickup_longitude)
    x += (math.cos(lat1)*math.cos(long1))
    y += (math.cos(lat1)*math.sin(long1))
    z += math.sin(lat1)
    #
    lat2,long2 = math.radians(cur_order.delivery_latitude), math.radians(cur_order.delivery_longitude)
    x += (math.cos(lat2)*math.cos(long2))
    y += (math.cos(lat2)*math.sin(long2))
    z += math.sin(lat2)
    #avg
    x /= 2
    y/= 2
    z/= 2
    #get mdpts in radians
    mdpt_long = math.degrees(math.atan2(y,x))
    mdpt_sqrt = math.sqrt(x*x + y*y)
    mdpt_lat = math.degrees(math.atan2(z, mdpt_sqrt))
    return render(request, 'trucker/confirm_order.html', {'order': cur_order, 'mid_long': mdpt_long, 'mid_lat': mdpt_lat})

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Accept_Order(request):
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        cur_order = order.objects.filter(id = jsn['order_id']).first()
        me = truck_company.objects.filter(user = request.user).first()
        cur_order.truck_company = me
        cur_order.status = 1
        cur_order.save()
        messages.info(request, "Order " + str(cur_order.customer_order_no) + " Accepted")
        return HttpResponseRedirect('/trucker')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Update_Status(request):
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        cur_order = order.objects.filter(id = jsn['order_id']).first()
        cur_order.status = int(jsn['status'])
        cur_order.save()
        return HttpResponseRedirect('/trucker')
