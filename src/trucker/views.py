from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from shipper.models import order, shipper, status_update, order_post_notification
from trucker.models import truck_company, trucks, driver, counter_offer
from authorization.decorators import allowed_users
from rest_framework.decorators import api_view
import json
import math
from django.contrib import messages
from authorization.models import Profile, User_Feedback
from friendship.models import FriendshipRequest, Friend, Follow
from django.contrib.auth.models import User
from CargoFul import settings
from trucker.file_storage import FileStorage
import os
from django.core.mail import send_mail
# Create your views here.

@login_required
@allowed_users(allowed_roles=['Trucker'])
def Available_Orders(request):
    if request.method == 'GET':
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
        my_orders = order.objects.filter(truck_company=me).exclude(status = 4).exclude(status = 5) #exclude delivered/cancelled orders
    return render(request, 'trucker/my_orders.html', {'my_orders': my_orders, 'me' : me, 'num_notifications': num_notifications})


@login_required
@allowed_users(allowed_roles=['Trucker'])
@api_view(['POST'])
def Confirm_Order(request):
    me = truck_company.objects.filter(user=request.user).first()
    connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
    order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
    counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
    num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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
        print(request.POST)
        me = truck_company.objects.filter(user=request.user).first()
        if 'counter_submit' in request.POST:
            print('True')
            jdp = json.dumps(request.data) #get request into json form
            jsn = json.loads(jdp) #get dictionary from json
            jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
            cur_order = order.objects.get(id=jsn['order_id'])
            offer = counter_offer(trucker_user = me, order = cur_order, counter_price = jsn['counter_price'])
            offer.save()
            return HttpResponseRedirect('/trucker')

        elif 'big_submit' in request.POST:
            print('BIG SUBMIT')
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
    me = truck_company.objects.filter(user=request.user).first()
    connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
    order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
    counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
    num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
        return render(request, 'trucker/notifications.html', {'requests': connect_requests, 'order_notifications': order_notifications, 'counter_offers': counter_offers, 'me': me, 'num_notifications': num_notifications})

#this method is for when a trucker views an order from the notification page, so the order is shown, but the notification must also be removed from
#the truckers set
@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def read_show_order_notification(request):
    if request.method == "POST":
        print('read_show_order_notification called')
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
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

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def read_counter_offer(request):
    if request.method == "POST":
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        c_o_notification = counter_offer.objects.get(id = jsn['counter_offer_id'])
        c_o_notification.status = 3
        c_o_notification.save()
        return HttpResponseRedirect("/trucker/notifications")

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['GET'])
def past_orders(request):
    if request.method == "GET":
        me = truck_company.objects.filter(user=request.user).first()
        connect_requests = FriendshipRequest.objects.filter(to_user=request.user) #query pending connections
        order_notifications = order_post_notification.objects.filter(truckers = request.user) #query all order notifications associated w/ the user
        counter_offers = counter_offer.objects.filter(trucker_user = me).exclude(status = 0).exclude(status = 3)
        num_notifications = len(list(connect_requests)) + len(list(order_notifications)) + len(list(counter_offers))
        #end notification number
        past_orders = order.objects.filter(truck_company = me).filter(status = 4)
        return render(request, 'trucker/past_orders.html', {'set': past_orders})


@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['POST'])
def get_feedback(request):
    if request.method == "POST":
        jdp = json.dumps(request.data) #get request into json form
        jsn = json.loads(jdp) #get dictionary from json
        jsn.pop("csrfmiddlewaretoken") #remove unnecessary stuff
        user = request.user
        feedback = User_Feedback(user = user, feedback = jsn['feedback'])
        feedback.save()
        messages.info(request, "Thank you for your feedback!")
        return HttpResponseRedirect('/trucker')

@login_required
@allowed_users(allowed_roles = ['Trucker'])
@api_view(['GET', 'POST'])
def upload_docs(request):
    if request.method == 'GET':
        return render(request, 'trucker/upload_docs.html')
    else:
        print(request.FILES)
        files_dir = 'docs/{user}'.format(user = "CF" + str(request.user.id))
        file_storage = FileStorage()
        for file in request.FILES: #loop through files in request
            doc = request.FILES[file] #get file
            doc_path = os.path.join(files_dir, file) #set path for file to be stored in
            file_storage.save(doc_path, doc)
        me = truck_company.objects.filter(user=request.user).first()
        me.docs_uploaded = True
        me.save()
        messages.info(request, "Gracias por Subir sus Documentos")
        #send trucker an email with some info
        current_user = request.user
        username = current_user.username
        email = current_user.email

        out_message = """Dear """ +  str(username) + """,
Thank you for uploading your documents to the platform!

Our team is reviewing them, you will be notified once your account is approved!
Please check your email frequently, as we may reach out for clarifications.

Relax now that you can - you will not have anymore idle times with Cargoful!
Your Cargoful team

Any questions? Don't hesitate to contact us at help@cargoful.org"""

        send_mail(
        'Thank you for uploading your documents! ', #email subject
        out_message, #email content
        'help@cargoful.org',
        [email],
        fail_silently = False,
        )
        return HttpResponseRedirect("/trucker")
