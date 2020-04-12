from django.urls import path
from . import views

urlpatterns = [
    path('', views.See_Dashboard, name = 'Dashboard'),
    path('approve_user', views.Approve_User, name = 'Approve_User'),
    path('approve_order', views.Approve_Order, name = 'Approve_Order'),
    path('accept_order', views.Accept_Order, name = 'Accept_Order'),
]
