from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from shipper.models import order, shipper
from trucker.models import truck_company
from authorization.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from authorization.decorators import allowed_users

from itertools import chain
import json
import math
from django.contrib import messages


# Create your views here.
@login_required
@allowed_users(allowed_roles=['Cf_admin'])
def See_Dashboard(request):
    #first check that request is a GET
    if request.method == "GET":
        new_users = Profile.objects.filter(is_approved = False)
        new_orders = order.objects.filter(is_approved = False)
        return render(request, 'cf_admin/dashboard.html', {'users' : new_users, 'orders': new_orders})

@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Approve_User(request):
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        user_profile = Profile.objects.get(id=jsn['profile_id'])
        print('User Profile', user_profile)
        user_profile.is_approved = True
        user_profile.save()
        messages.info(request, str(user_profile.company_name) + " successfully approved")
        return HttpResponseRedirect('/cf_admin')


@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Approve_Order(request):
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        order_id = jsn['order_id']
        cur_order = order.objects.get(id=order_id)

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

        return render(request, 'cf_admin/confirm_order.html', {'order' : cur_order, 'mid_long': mdpt_long, 'mid_lat': mdpt_lat})


@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Accept_Order(request):
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
    cur_order = order.objects.get(id=jsn['order_id'])
    cur_order.is_approved = True
    cur_order.status = 1
    cur_order.save()
    messages.success(request, "Order " + str(cur_order.customer_order_no) + " successfully approved")
    return HttpResponseRedirect('/cf_admin')

@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Delete_User(request):
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
    profile = Profile.objects.get(id=jsn['profile_id'])
    user = User.objects.get(id=profile.user.id)
    user.delete()
    messages.info(request, str(profile.company_name) + " successfully deleted")
    return HttpResponseRedirect('/cf_admin')

@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Delete_Order(request):
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
    cur_order = order.objects.get(id=jsn['order_id'])
    cur_order.delete()
    messages.info(request, str(cur_order.customer_order_no) + " successfully deleted")
    return HttpResponseRedirect('/cf_admin')
