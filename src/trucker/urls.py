from django.urls import path
from . import views

urlpatterns = [
    path('available_orders/', views.Available_Orders),
    path('', views.My_Orders),
    path('accept_order', views.Confirm_Order),
    path('update_status', views.Update_Status),
    path('order_accepted', views.Accept_Order),
    path('connection_requests', views.Show_Connects),
    path('accept_request', views.Accept_Connect),
    path('deny_request', views.Deny_Connect),
    path('search_shippers', views.Search_Shippers),
    path('send_connection_request_tr', views.Send_Connection_Request),
    path('notifications', views.show_notifications),
    path('read_show_order_notification', views.read_show_order_notification), #this url is for viewing an order from notification tab
    path('read_order_notification', views.read_order_notification), #this url is for just reading the notification (making it go away)
    path('read_counter_offer_notification', views.read_counter_offer), #this url is for making a counter offer notification go away
    path('past_orders', views.past_orders), #this is for showing past orders
]
