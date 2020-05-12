from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CreateUserForm, ProfileForm, EditUserInfo, PasswordChangeFormCustom
from .models import Profile
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from shipper.models import shipper
from .decorators import allowed_users
from friendship.models import FriendshipRequest, Friend, Follow
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.template.loader import get_template
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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
            email = form.cleaned_data.get('email')
            # messages.success(request, 'Account was created for ' + username)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # return settings.LOGIN_REDIRECT_URL
                messages.success(request, _("Welcome to CargoFul ") + str(username) + "!")
                #send email for email verification
                current_site = get_current_site(request)
                # message = render_to_string('registration/confirm_email.html', {
                # 'user': user,
                # 'domain': current_site.domain,
                # 'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                # 'token':account_activation_token.make_token(user),
                # })
                # send_mail(
                # 'Please verify your Cargoful account email!', #email subject
                # message, #email content
                # 'hellofromcargoful@gmail.com',
                # [email],
                # fail_silently = False,
                # )

                subject, from_email, to = '¡Ya casi eres parte de Cargoful! Verifica tu correo por favor', settings.EMAIL_HOST_USER, email
                text_content = render_to_string('emails/confirm_email/confirm_email_ES_txt.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
                })
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                html_template = get_template("emails/confirm_email/confirm_email_ES.html").render({
                                            'username': user.username,
                                            'domain': current_site.domain,
                                            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                            'token':account_activation_token.make_token(user),
                                            })
                msg.attach_alternative(html_template, "text/html")
                msg.send()
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
            messages.info(request, _('Username or Password is incorrect'))
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

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print("username is")
        print(user.username)
        print("company_name is")
        print(user.profile.company_name)
        #profile = user.get_profile()
        #user_profile = Profile.objects.get(id=jsn['profile_id'])
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        print("here")
        #user.email_confirmed = True
        user.profile.email_confirmed = True
        print(user.profile.email_confirmed)
        print("here2")
        user.profile.save()
        # login(request, user)
        # return redirect('home')
        return HttpResponseRedirect('/../../email_confirmed')#HttpResponse('Thank you for your email confirmation. You can now ...')
    else:
        return HttpResponse('Activation link is invalid!')

def email_confirmed(request):
    return render(request, 'registration/email_confirmed.html')

def set_language_en(request):
    user_language = 'en-us'
    translation.activate(user_language)
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/accounts/login'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
    return response


def set_language_es(request):
    user_language = 'es-mx'
    translation.activate(user_language)
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/accounts/login'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
    return response

def editProfileView(request):
    if request.method == "POST":
        user = request.user
        if "info_submit" in request.POST: #they changed profile info
            form = EditUserInfo(request.POST)
            print("here 1")
            print(form.errors)
            if form.is_valid():
                print("here")
                cd = form.cleaned_data
                if len(cd['first_name']) > 0:
                    user.first_name = cd['first_name']
                if len(cd['last_name']) > 0:
                    user.last_name = cd['last_name']
                if len(cd['email']) > 0:
                    user.email = cd['email']
                if len(cd['company_name']) > 0:
                    user.profile.company_name = cd['company_name']
                if len(cd['username']) > 0:
                    user.username = cd['username']
                user.save()
                messages.info(request, "Profile information successfully updated!")
            else:
                pform = PasswordChangeFormCustom(user = request.user)
                return render(request,'profiles/edit_profile.html',{'form':form,'pform': pform})
        else: #they changed their password
            pform = PasswordChangeFormCustom(user=request.user, data=request.POST)
            if pform.is_valid():
                pform.save()
                update_session_auth_hash(request, pform.user)
                messages.info(request, "Password successfully updated!")
            else:
                form = EditUserInfo()
                return render(request,'profiles/edit_profile.html',{'form':form,'pform': pform})
        if user.profile.user_type == "Shipper":
            return HttpResponseRedirect('/shipper')
        else:
            return HttpResponseRedirect('/trucker')
    form = EditUserInfo()
    pform = PasswordChangeFormCustom(user = request.user)
    return render(request,'profiles/edit_profile.html',{'form':form,'pform': pform})
