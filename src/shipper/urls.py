from django.urls import path
from . import views

urlpatterns = [
    path('', views.see_dashboard, name = 'dashboard'), #any url ending with /shipper/ then loads the views.py index() method
    path('post_order', views.post_order, name = 'post_order'), #url for posting new order
    path('confirmation', views.confirm, name = 'confirm'), #this url is the intermediate step before posting an order
    path('order_placed', views.order_success, name = 'order_placed'), #this url is for when an order has been confirmed
]
