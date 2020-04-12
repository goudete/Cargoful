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
]
