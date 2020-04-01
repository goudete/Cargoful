from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import Order_Form
from .models import order, shipper
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse
import json
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io
from rest_framework.decorators import api_view
from authorization.decorators import allowed_users
import googlemaps
from decimal import Decimal
import math
from haversine import haversine, Unit
from time import sleep
from django.contrib import messages
# Create your views here.

@login_required
@allowed_users(allowed_roles=['Shipper'])
@api_view(['POST', 'GET'])
def post_order(request):
    #if the method is a POST, then a user is editing an order from the confirmation page
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        #getting order specs
        pu_addy, del_addy = jsn['pickup_address'], jsn['delivery_address']
        date, time = jsn['pickup_date'], jsn['pickup_time']
        #format time
        if int(time.split(":")[0]) >= 12:
            time = str(int(time.split(":")[0]) -12) + ":" +str(time.split(":")[1]) + " PM"
        else:
            time = str(time) + " AM"
        #other specs
        truck, price = jsn['truck_type'], jsn['price']
        contents, instructions = jsn['contents'], jsn['instructions']
        #render a copy of order form (different HTML file b/c there is no crispy forms)
        TRUCK_TYPES = [
            ('Low Boy', 'Low Boy'),
            ('Caja Seca 48 pies', 'Caja Seca 48 pies'),
            ('Refrigerado 48 pies', 'Refrigerado 48 pies'),
            ('Plataforma 48 pies', 'Plataforma 48 pies'),
            ('Caja Seca 53 pies', 'Caja Seca 53 pies'),
            ('Refrigerado 53 pies', 'Refrigerado 53 pies'),
            ('Plataforma 53 pies', 'Plataforma 53 pies'),
            ('Full', 'Full'),
            ('Plataforma Full', 'Plataforma Full'),
            ('Torton Caja Seca', 'Torton Caja Seca'),
            ('Torton Refrigerado', 'Torton Refrigerado'),
            ('Troton Plataforma', 'Troton Plataforma'),
            ('Rabon Caja Seca', 'Rabon Caja Seca'),
            ('Rabon Refrigerado', 'Rabon Refrigerado'),
            ('Rabon Plataforma', 'Rabon Plataforma'),
            ('Camioneta 5.5 tons', 'Camioneta 5.5 tons'),
            ('Camioneta 3.5 tons', 'Camioneta 3.5 tons'),
            ('Camioneta 3.5 tons Plataforma', 'Camioneta 3.5 tons Plataforma'),
            ('Camioneta 1.5 tons', 'Camioneta 1.5 tons'),
            ('Camioneta 3.5 tons Redilla', 'Camioneta 3.5 tons Redilla'),
        ] #this dict is for the dropdown menu for truck type
        return render(request, 'shipper/change_order.html',
        {
            'pu_addy': pu_addy,
            'del_addy': del_addy,
            'date': date,
            'time': time,
            'truck': truck,
            'truck_dict': TRUCK_TYPES,
            'price': price,
            'contents': contents,
            'instructions': instructions
        })
    #if the method is a get then the user is posting a new order for the first time
    else:
        order_form = Order_Form()
    return render(request, 'shipper/post_order.html', {'form': order_form})

#display shipper dashboard
@login_required
@allowed_users(allowed_roles=['Shipper'])
def see_dashboard(request):
    #first check that request is a GET
    if request.method == "GET":
        company = shipper.objects.filter(user = request.user).first() #this query gets the shipper
        set = order.objects.filter(shipping_company = company).order_by('status') #this query gets all jobs posted by the user in order from status 0 -> status 4
        return render(request, 'shipper/dashboard.html', {'set': set})

#intermediate confirmation step, once a shipper submits an order, they are sent here to confirm
@login_required
@allowed_users(allowed_roles=['Shipper'])
@api_view(['POST'])
def confirm(request):
    if request.method == "POST":
        """stuff for handling json inside request"""
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        print(jsn)
        #get necessary info
        #use googlemaps api to get lat and long for pickup and delivery
        gmaps = googlemaps.Client(key='AIzaSyCKmjFt91GOvHaqyxpoiiqFQURjFST7U2I')
        pu_address_full = jsn['pu_addy']
        del_address_full = jsn['del_addy']
        pu_geocode = gmaps.geocode(pu_address_full)
        del_geocode = gmaps.geocode(del_address_full)
        #get lat  and lng
        pu_lat = pu_geocode[0]['geometry']['location']['lat']
        pu_long = pu_geocode[0]['geometry']['location']['lng']
        del_lat = del_geocode[0]['geometry']['location']['lat']
        del_long = del_geocode[0]['geometry']['location']['lng']

        """lines 86 - 103 are for getting mdpt of two lat/lng coordinates"""
        x,y,z = 0,0,0
        lat1,long1 = math.radians(pu_lat), math.radians(pu_long)
        x += (math.cos(lat1)*math.cos(long1))
        y += (math.cos(lat1)*math.sin(long1))
        z += math.sin(lat1)
        #
        lat2,long2 = math.radians(del_lat), math.radians(del_long)
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
        """end mdpt calculation"""
        #get the distance btwn pickup and delivery
        distance = round(haversine((pu_lat,pu_long), (del_lat,del_long)), 4)
        #other regular metrics
        date = jsn['pickup_date']
        time = jsn['pickup_time']
        #account for time being in PM
        if time.split(" ")[1] == "PM":
            hour = int(time.split(" ")[0].split(":")[0])
            hour += 12
            time = str(hour) + ":" + time.split(" ")[0].split(":")[1]+" PM"
        print(time)
        #other specs
        truck = jsn['truck_type']
        cargo = jsn['contents']
        instructions = jsn['instructions']
        price = jsn['price']
    else:
        pass
    #long list of variables is for the html page, all of these will be displayed in the confirmation page
    return render(request, 'shipper/confirmation.html',
    {
        'pu_addy': pu_address_full,
        'del_addy': del_address_full,
        'pu_lat': pu_lat,
        'pu_long': pu_long,
        'del_lat': del_lat,
        'del_long': del_long,
        'mid_lat': mdpt_lat,
        'mid_long': mdpt_long,
        'distance': distance,
        'date':date,
        'time': time,
        'truck': truck,
        'cargo': cargo,
        'instruct': instructions,
        'price': price
    })

#if the order is confirmed, then this page is rendered, it saves the order to db
@login_required
@allowed_users(allowed_roles=['Shipper'])
@api_view(['POST'])
def order_success(request):
    #check if request is a post
    if request.method == "POST":
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
        #create order
        n_order = Order_Form(request.POST)
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
            new_order.distance = round(dist,3)
            new_order.save()
            messages.info(request, "Order "+ str(customer_order_no) + " Placed Successfully")
            return HttpResponseRedirect('/shipper')
