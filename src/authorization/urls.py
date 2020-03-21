from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('login_success/', views.login_success, name='login_success'),
    path('logout/', views.logout_view, name='logout')
]
