from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from shipper.models import order, shipper, order_post_notification
from trucker.models import truck_company
from authorization.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from authorization.decorators import allowed_users
from CargoFul import settings
import botocore
import boto3
from itertools import chain
import json
import math
from django.contrib import messages
from friendship.models import FriendshipRequest, Friend, Follow
import os
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from io import BytesIO
import zipfile



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
def Download_Docs(request):
    s3 = boto3.resource('s3') #setup to get from AWS
    jdp = json.dumps(request.data) #get request into json form
    jsn = json.loads(jdp) #get dictionary from json
    jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
    user_profile = Profile.objects.get(id=jsn['profile_id'])
    docs_user = user_profile.user #this refers to the user whose docs we are viewing
    #setup to download off AWS
    #create folder to store files
    aws_dir = os.path.join('docs/CF'+str(docs_user.id))
    #create zip file
    byte = BytesIO()
    zip = zipfile.ZipFile(byte, "w")
    zip_file_name = "Trucker-"+str(docs_user.id)+".zip"
    #download files
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    objs = bucket.objects.filter(Prefix=aws_dir) #get folder
    for obj in objs: #iterate over file objects in folder
        path, filename = os.path.split(obj.key)
        data = obj.get()['Body'].read()
        open(filename, 'wb').write(data)
        zip.write(filename) #write file to zip folder
        os.unlink(filename)
    zip.close()
    resp = HttpResponse(
        byte.getvalue(),
        content_type = "application/x-zip-compressed"
    )
    resp['Content-Disposition'] = 'attachment; filename = %s' % zip_file_name
    return resp


@login_required
@allowed_users(allowed_roles=['Cf_admin'])
@api_view(['POST'])
def Approve_User(request):
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        user_profile = Profile.objects.get(id=jsn['profile_id'])
        user_profile.is_approved = True
        user_profile.save()
        messages.info(request, str(user_profile.company_name) + _(" successfully approved"))
        #send them an email to let them know they're approved
        user = User.objects.get(id=jsn['profile_id'])
        email = user.email
        username = user.username
        send_mail(
        'Welcome to Cargoful!', #email subject, next arg is content
        ('Dear ' + str(username) + """, \n
        Your account has been approved - Welcome to Cargoful!  \n  \n
        Please login at the link below to get access to the latest shipments on the platform!  \n  \n
        http://34.216.209.104:8000/accounts/login/ \n \n
        Looking forward to many kms together!
        Your Carfogul team  \n  \n  \n  \n
        Any questions? Don't hesitate to contact us at help@cargoful.org"""),
        'help@cargoful.org',
        [email],
        fail_silently = False,
        )
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
    #send out a message to the shipper's connected truckers that this order is available
    notification = order_post_notification(order = cur_order)
    notification.save()
    shipper = cur_order.shipping_company #get the shipper associated w/ the order
    trucker_connection_list = Friend.objects.friends(shipper.user) #list of all truckers connected w/ that shipper
    #add those shippers to the notification
    for trucker in trucker_connection_list:
        notification.truckers.add(trucker)
    notification.save()
    #done w/ order notification for truckers
    messages.success(request, _("Order ") + str(cur_order.customer_order_no) + _(" successfully approved"))
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
    messages.info(request, str(profile.company_name) + _(" successfully deleted"))
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
    messages.info(request, str(cur_order.customer_order_no) + _(" successfully deleted"))
    return HttpResponseRedirect('/cf_admin')
