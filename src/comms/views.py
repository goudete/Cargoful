from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

def contactFormView(request):
    if request.method == "POST":
        query_dict = request.POST #request.data doesnt work for some reason

        customer_name = query_dict['name']
        email = query_dict['email']
        phone_number = query_dict['phone_number']
        website = query_dict['website']
        message = query_dict['message']

        if request.user.is_authenticated: #if user is logged in as shipper or trucker
            out_message = "Hi, " + customer_name + " has contacted the team with the following message: \n \n"
            out_message += message + "\n \n"
            out_message += "Get back to him at " + email + ". \n \n \n"

            user = request.user
            user_type = str(user.profile.user_type)
            out_message += "Additional user info:  \n \n"
            out_message += "username: " + str(user.username) + "\n"
            out_message += "user type: " + str(user.profile.user_type) + "\n"
            out_message += "registered email: " + user_type + "\n"
            if len(website) > 0:
                out_message += "given website: " + website + "\n"
            if len(phone_number) > 0:
                out_message += "given phone number: " + phone_number + "\n"
            send_mail(
            customer_name + ' HAS A NEW HELP REQUEST!', #email subject
            out_message, #email content
            'help@cargoful.org',
            ['help@cargoful.org'],
            fail_silently = False,
            )

            #send another mail confirming help is on the way
            send_mail(
            'Help is on the way!', #email subject
            """Dear """ + customer_name + """, \n
    Thank you for reaching out to the Cargoful team! \n
    We will review your message and get back to you soon. \n \n
    Never alone with Cargoful! \n
    Your Cargoful team \n \n
    Here your request: \n""" + message, #email content
            'help@cargoful.org',
            [email],
            fail_silently = False,
            )
            messages.info(request, "Thanks "+ str(customer_name)
            + "! We have received your message and will get back to you shortly at " + email)
            if user_type == "Shipper":
                return HttpResponseRedirect('/shipper')
            else:
                return HttpResponseRedirect('/trucker')
        else:
            out_message = """Hi, an unauthenticated user named """ + customer_name
            out_message += """has contacted the team with the following message: \n \n """
            out_message += message + "\n \n"
            out_message += "Get back to him at " + email + ". \n \n \n"
            if len(website) > 0:
                out_message += "given website: " + website + "\n"
            if len(phone_number) > 0:
                out_message += "given phone number: " + phone_number + "\n"
            send_mail(
            customer_name + ' HAS A NEW HELP REQUEST!', #email subject
            out_message, #email content
            'help@cargoful.org',
            ['help@cargoful.org'],
            fail_silently = False,
            )

            #send another mail confirming help is on the way
            send_mail(
            'Help is on the way!', #email subject
            """Dear """ + customer_name + """, \n
Thank you for reaching out to the Cargoful team! \n
We will review your message and get back to you soon. \n \n
Never alone with Cargoful! \n
Your Cargoful team \n \n
Here your request: \n""" + message, #email content
            'help@cargoful.org',
            [email],
            fail_silently = False,
            )
            return HttpResponseRedirect('/accounts/login')
    else:
        return render(request, 'contact_form.html')
