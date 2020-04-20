from django.urls import path
from . import views

urlpatterns = [
    path('', views.see_dashboard, name = 'dashboard'), #any url ending with /shipper/ then loads the views.py index() method
    path('post_order', views.post_order, name = 'post_order'), #url for posting new order
    path('confirmation', views.confirm, name = 'confirm'), #this url is the intermediate step before posting an order
    path('order_placed', views.order_success, name = 'order_placed'), #this url is for when an order has been confirmed
    path('search_truckers', views.show_truckers, name = 'search'), #this url is for when a shipper queries truckers
    path('connection_requests', views.show_connects), #this url is for when a shipper sees their connections
    path('accept_request', views.accept_request), #this url is for when a shipper accepts a connection from a trucker
    path('deny_request', views.deny_request), #this url is for when a trucker denies a request
    path('ajax/ajax_price_calculation', views.ajax_price_calculation, name = 'price_calculation'), #to calculate price
    path('send_connection_request', views.make_connection_request, name = 'request'), #this url is for making a new connection request between a shipper and trucker
    path('notifications', views.show_notifications), #this url is for showing the notification dashboard
    path('read_status_update', views.read_status_update), #this url is for reading a status update notification to make it go away
    path('accept_counter_offer', views.accept_counter_offer), #this url is for accepting a counter offer from trucker
    path('review_counter_offer', views.review_counter_offer), #this url is for seeing an order from the counter offer notification
    path('deny_counter_offer', views.deny_counter_offer), #this url is for denying a counter offer
    path('past_orders', views.show_past_orders), #this url is for showing past orders (already delivered)
]
