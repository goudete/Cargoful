from django.urls import path
from . import views

urlpatterns = [
    path('available_orders/', views.Available_Orders),
    path('', views.My_Orders),
    path('accept_order', views.Confirm_Order),
    path('update_status', views.Update_Status),
    path('order_accepted', views.Accept_Order),
]
