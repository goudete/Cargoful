from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from shipper.models import order, shipper
from trucker.models import truck_company, trucks, driver
from authorization.decorators import allowed_users
from rest_framework.decorators import api_view
import json
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
def Accept_Order(request, orderID):
    #post to db and remove from available jobs
    # POST truck_company , status change to 1
    me = truck_company.objects.filter(user=request.user).first()
    cur_order = order.objects.filter(id=orderID).first()
    cur_order.truck_company = me
    cur_order.status = 1
    cur_order.save()
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
