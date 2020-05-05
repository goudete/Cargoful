from django.urls import path
from . import views

urlpatterns = [
    path('', views.See_Dashboard, name = 'Dashboard'),
    path('approve_user', views.Approve_User, name = 'Approve_User'),
    path('approve_order', views.Approve_Order, name = 'Approve_Order'),
    path('accept_order', views.Accept_Order, name = 'Accept_Order'),
    path('delete_user', views.Delete_User, name = 'Delete_User'),
    path('delete_order', views.Delete_Order, name = 'Delete_Order'),
    path('download', views.Download_Docs), #for reviewing a trucker and looking at their docs
    path('download_orden_de_embarco', views.download_orden_de_embarco), #for downloading embarco
    path('view_orden_de_embarco', views.view_orden_de_embarco), #for viewing embarco on new page
]
