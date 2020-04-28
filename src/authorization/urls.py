from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('login_success/', views.login_success, name='login_success'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('email_confirmed/',views.email_confirmed, name = "email_confirmed"),
    path('set_language_en', views.set_language_en, name='set_language_en'),
    path('set_language_es', views.set_language_es, name='set_language_es'),
    ]
