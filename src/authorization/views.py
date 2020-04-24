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
from friendship.models import FriendshipRequest, Friend, Follow

def register_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # making all truckers automatically connected w/ cargoful
            if profile.user_type == 'Trucker':
                cargoful_shipper = Profile.objects.filter(company_name = "Cargoful").filter(user_type = "Shipper").first().user #get the user associated w/ cargoful shipper
                Friend.objects.add_friend(cargoful_shipper, user) #send a freind request form cargoful to the trucker
                req = FriendshipRequest.objects.get(to_user = user) #get the request again to accept it
                req.accept() #accept it
                Follow.objects.add_follower(user, req.from_user) #make it so that they are connected both ways
            #end cargoful connect block

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # messages.success(request, 'Account was created for ' + username)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # return settings.LOGIN_REDIRECT_URL
                messages.success(request, "Welcome to CargoFul " + str(username) + "!")
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
        elif usertype == 'Cf_admin':
            return redirect('/cf_admin')
        else:
            return HttpResponse('Have yet to develop Driver View! :)')


def logout_view(request):
    logout(request)
    return redirect('/accounts/login')
    #minuto 30:11 https://www.youtube.com/watch?v=tUqUdu0Sjyc

def home_view(request):
    return render(request, 'registration/home.html')
