from django.http import HttpResponse
from django.shortcuts import redirect

#decorator that wrapps view functions. Depending on Group membership, allows
#or restricts access.
#For reference: https://www.youtube.com/watch?v=eBsc65jTKvw&t=662s
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')
        return wrapper_func
    return decorator


#This decorator is supposed to not let logged in users access login and register pages.
#Not working. Eventually need to fix this. 
# def unautheticated_user(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             usertype = request.user.profile.user_type
#             if user_type == 'Shipper':
#                 return redirect('/shipper')
#             elif user_type == 'Trucker':
#                 return redirect('/trucker')
#             else:
#                 #eventually redirect to driver homepage
#                 return HttpResponse('Driver already logged in! :)')
#         else:
#             return view_func(request, *args, **kwargs)
#     return wrapper_func
