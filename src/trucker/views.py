from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from shipper.models import order, shipper, status_update, order_post_notification
from trucker.models import truck_company, trucks, driver
from authorization.decorators import allowed_users
from rest_framework.decorators import api_view
import json
import math
from django.contrib import messages
from authorization.models import Profile
from friendship.models import FriendshipRequest, Friend, Follow
from django.contrib.auth.models import User
# Create your views here.

@login_required
@allowed_users(allowed_roles=['Trucker'])
def Available_Orders(request):
    if request.method == 'GET':
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        me = truck_company.objects.filter(user=request.user).first()
        connections = Friend.objects.friends(request.user) #get the current shippers connected w/ this trucker
        avail = order.objects.filter(status__exact=1) #all available orders
        available = [] #list of orders posted by shippers connected with trucker
        for a in avail:
            if a.shipping_company.user in connections:
                available.append(a)
        return render(request, 'trucker/available_orders.html', {'available': available, 'me' : me, 'num_notifications': num_notifications})


@login_required
@allowed_users(allowed_roles=['Trucker'])
def My_Orders(request):
    if request.method == 'GET':
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        me = truck_company.objects.filter(user=request.user).first()
        my_orders = order.objects.filter(truck_company=me)
    return render(request, 'trucker/my_orders.html', {'my_orders': my_orders, 'me' : me, 'num_notifications': num_notifications})


@login_required
@allowed_users(allowed_roles=['Trucker'])
@api_view(['POST'])
def Confirm_Order(request):
    connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
    order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
    #counter offer query goes here (if they said yes or no I guess)
    num_notifications = len(list(connect_requests)) + len(list(order_notifications))
    me = truck_company.objects.filter(user=request.user).first()
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
    return render(request, 'trucker/confirm_order.html', {'order': cur_order, 'mid_long': mdpt_long, 'mid_lat': mdpt_lat, 'me' : me, 'num_notifications': num_notifications})

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Accept_Order(request):
    if request.method == 'POST':
        me = truck_company.objects.filter(user=request.user).first()
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        cur_order = order.objects.filter(id = jsn['order_id']).first()
        cur_order.truck_company = me
        cur_order.status = 2
        cur_order.save()
        #create new status update notification for shipper
        s_u = status_update.objects.create(trucker = me, shipper = cur_order.shipping_company, old_status = 1, new_status = 2, order = cur_order, read = False)
        s_u.save()
        messages.info(request, "Order " + str(cur_order.customer_order_no) + " Accepted")
        return HttpResponseRedirect('/trucker')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Update_Status(request):
    if request.method == 'POST':
        me = truck_company.objects.filter(user=request.user).first()
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        cur_order = order.objects.filter(id = jsn['order_id']).first()
        #creating new status_update message for shipper
        if cur_order.status < int(jsn['status']):
            s_u = status_update.objects.create(trucker = me, shipper = cur_order.shipping_company, old_status = cur_order.status, new_status = int(jsn['status']), order = cur_order, read = False)
            s_u.save()
        #update order status field
        cur_order.status = int(jsn['status'])
        cur_order.save()
        return HttpResponseRedirect('/trucker')

@login_required
@allowed_users(allowed_roles=['Trucker'])
def Show_Connects(request):
    connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
    order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
    #counter offer query goes here (if they said yes or no I guess)
    num_notifications = len(list(connect_requests)) + len(list(order_notifications))
    me = truck_company.objects.filter(user=request.user).first()
    connections = list(Friend.objects.friends(request.user)) #query existing connections
    pending_connects = Friend.objects.sent_requests(user=request.user)  #list of connections you have sent
    pending = [] #the list of recipients of the connects in pending_connects
    #get the recipients
    for p in pending_connects:
        if Friend.objects.are_friends(request.user, p.to_user):
            continue #if users are already friends disregard
        elif p in Friend.objects.rejected_requests(user=p.to_user):
            continue #if user rejected connection disregard
        else:
            connections.append(p.to_user)
            pending.append(p.to_user)
    return render(request, 'trucker/connects.html', {'pending': pending, 'connections': connections, 'me' : me, 'num_notifications': num_notifications})

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Accept_Connect(request):
    if request.method == 'POST':
        me = truck_company.objects.filter(user=request.user).first()
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        req = FriendshipRequest.objects.get(id = jsn['request_id'])
        req.accept()
        Follow.objects.add_follower(request.user, req.from_user)
        messages.info(request, "Connection from " + str(req.from_user.profile.company_name) + " Accepted")
        return HttpResponseRedirect('/trucker/connection_requests')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Deny_Connect(request):
    if request.method == 'POST':
        me = truck_company.objects.filter(user=request.user).first()
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        req = FriendshipRequest.objects.get(id = jsn['request_id'])
        req.reject()
        req.delete()
        return HttpResponseRedirect('/trucker/connection_requests')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST', 'GET'])
def Search_Shippers(request):
    me = truck_company.objects.filter(user=request.user).first()
    if request.method == 'POST':
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        query = jsn['query'] #what was queried in searchbar
        #get a query set of truckers for the searchbar
        connection_list = Friend.objects.friends(request.user) #list of ppl user already connected with
        pending_connects = Friend.objects.sent_requests(user=request.user)  #list of connections you have sent
        pending = [] #the list of recipients of the connects in pending_connects
        #get the recipients
        for p in pending_connects:
            if Friend.objects.are_friends(request.user, p.to_user):
                continue #if users are already friends disregard
            elif p in Friend.objects.rejected_requests(user=p.to_user):
                continue #if user rejected connection disregard
            else:
                pending.append(p.to_user)
        #get the ppl whose company names match your query
        query_set = []
        queries = query.split(" ") #turns a search like "trucking company" -> [trucking, company]
        for word in queries:
            truckers = Profile.objects.filter(user_type = "Shipper").filter(company_name__icontains = word).distinct() #get truckers that have any of the words in company name
            for trucker in truckers:
                query_set.append(trucker)
        return render(request, 'trucker/search_connections.html', {'shippers': set(query_set), 'connects': connection_list, 'pending': pending, 'me' : me, 'num_notifications': num_notifications})
    #if the request is a GET, then the user wants to see all shippers on the platform
    else:
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        connection_list = Friend.objects.friends(request.user) #list of ppl user already connected with
        pending_connects = Friend.objects.sent_requests(user=request.user)  #list of connections you have sent
        pending = [] #the list of recipients of the connects in pending_connects
        #get the recipients
        for p in pending_connects:
            if Friend.objects.are_friends(request.user, p.to_user):
                continue #if users are already friends disregard
            elif p in Friend.objects.rejected_requests(user=p.to_user):
                continue #if user rejected connection disregard
            else:
                pending.append(p.to_user)
        shippers = Profile.objects.filter(user_type = "Shipper")
        return render(request, 'trucker/search_connections.html', {'shippers': set(shippers), 'connects': connection_list, 'pending': pending, 'me' : me, 'num_notifications': num_notifications})

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def Send_Connection_Request(request):
    me = truck_company.objects.filter(user=request.user).first()
    if request.method == 'POST':
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        receiver = User.objects.filter(id = jsn['shipper_id']).first() #get recipient of request
        sender = request.user
        Friend.objects.add_friend(sender, receiver) #send 'friend request' which in this case is a connection request
        messages.info(request, "Requested Connection With "+ str(receiver.profile.company_name))
        return HttpResponseRedirect('/trucker')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['GET'])
def show_notifications(request):
    if request.method == "GET":
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        return render(request, 'trucker/notifications.html', {'requests': connect_requests, 'order_notifications': order_notifications, 'me': me, 'num_notifications': num_notifications})

#this method is for when a trucker views an order from the notification page, so the order is shown, but the notification must also be removed from
#the truckers set
@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def read_show_order_notification(request):
    if request.method == "POST":
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        #counter offer query goes here (if they said yes or no I guess)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications))
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        #1st remove notification from trucker dash
        notification = order_post_notification.objects.get(id = jsn['notification_id'])
        notification.truckers.remove(request.user)
        #then display order
        cur_order = order.objects.get(id=jsn['order_id'])
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
        return render(request, 'trucker/confirm_order.html', {'order': cur_order, 'mid_long': mdpt_long, 'mid_lat': mdpt_lat, 'me' : me, 'num_notifications': num_notifications})


#this method is for when a trucker just wants a new order notification to go away
@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def read_order_notification(request):
    if request.method == "POST":
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        #1st remove notification from trucker dash
        notification = order_post_notification.objects.get(id = jsn['notification_id'])
        notification.truckers.remove(request.user)
        return HttpResponseRedirect("/trucker/notifications")
