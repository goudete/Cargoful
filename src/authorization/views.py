from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CreateUserForm, ProfileForm
from .models import Profile
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from shipper.models import shipper
from .decorators import allowed_users

def register_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # messages.success(request, 'Account was created for ' + username)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # return settings.LOGIN_REDIRECT_URL
                return redirect('/login_success')
    else:
        form = CreateUserForm()
        profile_form = ProfileForm()

    context = {'form' : form, 'profile_form' : profile_form}
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return settings.LOGIN_REDIRECT_URL

        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect('/accounts/login')

    context = {}
    return render(request, 'registration/login.html', context)

def login_success(request):
    if request.method == 'GET':
        usertype = request.user.profile.user_type
        if usertype == 'Shipper':
            return redirect('/shipper')
        elif usertype == 'Trucker':
            return redirect('/trucker')
        else:
            return HttpResponse('Have yet to develop Driver View! :)')


def logout_view(request):
    logout(request)
    return redirect('/accounts/login')
    #minuto 30:11 https://www.youtube.com/watch?v=tUqUdu0Sjyc
